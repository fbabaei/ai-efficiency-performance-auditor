#!/usr/bin/env bash
set -euo pipefail

target_repo_path=""
target_repo_url=""
source_repo_path=""
source_repo_url="https://github.com/fbabaei/ai-efficiency-performance-auditor.git"
include_service_performance_skill=0
interactive=0
audit_focus="latency, token/tool-call efficiency, retries"
audit_email_recipient=""
include_teams_notification=1
skills=()

usage() {
  cat <<'EOF'
Usage:
  bootstrap-auditor.sh [options]

Options:
  --target-repo-path <path>     Local target application repository path
  --target-repo-url <url>       Target application repository URL (cloned if missing)
  --source-repo-path <path>     Local source path of ai-efficiency-performance-auditor
  --source-repo-url <url>       Source repository URL (default: fbabaei/ai-efficiency-performance-auditor)
  --skill <name>                Optional skill folder to copy (repeatable)
  --include-service-performance-skill
                                Also copy service-performance-review skill
  --interactive                 Prompt for missing values and output ready Scout command
  --audit-focus <text>          Focus text for generated Scout command
  --audit-email-recipient <mail>
                                Optional email recipient for generated Scout command
  --no-teams-notification       Do not include "and teams" in generated Scout command
  -h, --help                    Show this help

Existing install paths are never overwritten. Move them aside before reinstalling.

Examples:
  ./scripts/bootstrap-auditor.sh \
    --target-repo-url https://github.com/contoso/my-app.git \
    --include-service-performance-skill

  ./scripts/bootstrap-auditor.sh \
    --target-repo-path /workspace/my-app \
    --skill context-retrieval-review \
    --skill orchestration-efficiency-review
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target-repo-path)
      target_repo_path="${2:-}"; shift 2 ;;
    --target-repo-url)
      target_repo_url="${2:-}"; shift 2 ;;
    --source-repo-path)
      source_repo_path="${2:-}"; shift 2 ;;
    --source-repo-url)
      source_repo_url="${2:-}"; shift 2 ;;
    --skill)
      skills+=("${2:-}"); shift 2 ;;
    --include-service-performance-skill)
      include_service_performance_skill=1; shift ;;
    --interactive)
      interactive=1; shift ;;
    --audit-focus)
      audit_focus="${2:-}"; shift 2 ;;
    --audit-email-recipient)
      audit_email_recipient="${2:-}"; shift 2 ;;
    --no-teams-notification)
      include_teams_notification=0; shift ;;
    -h|--help)
      usage; exit 0 ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 1 ;;
  esac
done

if ! command -v git >/dev/null 2>&1; then
  echo "git is required but was not found in PATH." >&2
  exit 1
fi

prompt_if_empty() {
  local current="$1"
  local prompt="$2"
  if [[ -n "$current" ]]; then
    echo "$current"
    return
  fi
  read -r -p "$prompt: " input
  echo "$input"
}

yes_default_true() {
  local prompt="$1"
  local answer
  read -r -p "$prompt (Y/n): " answer
  answer="$(printf '%s' "$answer" | tr '[:upper:]' '[:lower:]')"
  if [[ -z "$answer" || "$answer" == "y" || "$answer" == "yes" ]]; then
    return 0
  fi
  return 1
}

ensure_directory() {
  mkdir -p -- "$1"
}

fail() {
  printf '%s\n' "$*" >&2
  exit 1
}

valid_path_name() {
  local LC_ALL=C
  [[ "$1" =~ ^[a-zA-Z0-9][a-zA-Z0-9._-]*$ && "$1" != *. ]] &&
    [[ ! "$1" =~ ^([Cc][Oo][Nn]|[Pp][Rr][Nn]|[Aa][Uu][Xx]|[Nn][Uu][Ll]|[Cc][Oo][Mm][1-9]|[Ll][Pp][Tt][1-9])(\.|$) ]]
}

is_repo_root() {
  local info
  info="$(git -C "$1" rev-parse --is-inside-work-tree --show-prefix 2>/dev/null)" &&
    [[ "$info" == true ]]
}

check_directory() {
  local path="$1"
  if [[ -L "$path" || ( -e "$path" && ! -d "$path" ) ]]; then
    fail "Expected a real directory, not a link or other entry: $path"
  fi
}

check_new_path() {
  if [[ -e "$1" || -L "$1" ]]; then
    fail "Install path already exists; move it aside before rerunning: $1"
  fi
}

resolve_repo_name() {
  local url="$1"
  local trimmed="${url%/}"
  local name
  name="$(basename -- "$trimmed")"
  name="${name%.git}"
  if ! valid_path_name "$name"; then
    echo "Could not infer repository name from URL: $url" >&2
    exit 1
  fi
  echo "$name"
}

ensure_repo() {
  local local_path="$1"
  local repo_url="$2"
  check_directory "$local_path"
  if [[ -d "$local_path" ]]; then
    if ! is_repo_root "$local_path"; then
      echo "Path exists but is not a git repository: $local_path" >&2
      exit 1
    fi
    echo "Updating repository: $local_path"
    git -C "$local_path" pull --ff-only
    return
  fi
  ensure_directory "$(dirname -- "$local_path")"
  echo "Cloning repository: $repo_url -> $local_path"
  git clone -- "$repo_url" "$local_path"
}

working_root="${HOME}/workspace"

if [[ -z "$target_repo_path" && -z "$target_repo_url" ]]; then
  if [[ "$interactive" -ne 1 ]]; then
    echo "Provide --target-repo-path or --target-repo-url, or run with --interactive." >&2
    exit 1
  fi
fi

if [[ "$interactive" -eq 1 ]]; then
  if [[ -z "$target_repo_path" && -z "$target_repo_url" ]]; then
    echo "Choose target mode:"
    echo "  1) GitHub repository URL"
    echo "  2) Local repository path"
    read -r -p "Enter 1 or 2: " mode
    if [[ "$mode" == "1" ]]; then
      target_repo_url="$(prompt_if_empty "$target_repo_url" "Target repository URL")"
    elif [[ "$mode" == "2" ]]; then
      target_repo_path="$(prompt_if_empty "$target_repo_path" "Target local repository path")"
    else
      echo "Invalid selection. Enter 1 or 2." >&2
      exit 1
    fi
  fi

  if [[ "$include_service_performance_skill" -eq 0 ]] && yes_default_true "Include service-performance-review skill?"; then
    include_service_performance_skill=1
  fi

  if [[ -z "${skills[0]+x}" ]]; then
    read -r -p "Additional skills (comma-separated, optional): " extra_skills
    if [[ -n "${extra_skills// }" ]]; then
      IFS=',' read -r -a parsed <<< "$extra_skills"
      for item in "${parsed[@]}"; do
        item="$(printf '%s' "$item" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
        [[ -n "$item" ]] && skills+=("$item")
      done
    fi
  fi

  read -r -p "Audit focus (default: ${audit_focus}): " focus_input
  if [[ -n "${focus_input// }" ]]; then
    audit_focus="$focus_input"
  fi

  read -r -p "Email recipient for Scout delivery (optional): " recipient_input
  if [[ -n "${recipient_input// }" ]]; then
    audit_email_recipient="$recipient_input"
  fi

  if ! yes_default_true "Include Teams notification in Scout command?"; then
    include_teams_notification=0
  fi
fi

if [[ "$include_service_performance_skill" -eq 1 ]]; then
  skills+=("service-performance-review")
fi

validate_skill_name() {
  local LC_ALL=C
  if ! valid_path_name "$1" || [[ ! "$1" =~ ^[a-z0-9][a-z0-9-]*$ ]]; then
    fail "Invalid skill name '$1': use lowercase ASCII letters, digits and hyphens, starting with a letter or digit."
  fi
}

unique_skills=()
if [[ -n "${skills[0]+x}" ]]; then
  for skill_name in "${skills[@]}"; do
    validate_skill_name "$skill_name"
  done
  while IFS= read -r skill_name; do
    unique_skills+=("$skill_name")
  done < <(printf '%s\n' "${skills[@]}" | awk '!seen[$0]++')
fi

resolved_audit_target=""
if [[ -z "$target_repo_path" ]]; then
  target_name="$(resolve_repo_name "$target_repo_url")"
  target_repo_path="${working_root}/${target_name}"
  ensure_repo "$target_repo_path" "$target_repo_url"
  resolved_audit_target="$target_repo_url"
elif ! is_repo_root "$target_repo_path"; then
  echo "Target path is not a git repository: $target_repo_path" >&2
  exit 1
else
  resolved_audit_target="$target_repo_path"
fi

if [[ -z "$source_repo_path" ]]; then
  source_name="$(resolve_repo_name "$source_repo_url")"
  source_repo_path="${working_root}/${source_name}"
  ensure_repo "$source_repo_path" "$source_repo_url"
elif ! is_repo_root "$source_repo_path"; then
  echo "Source path is not a git repository: $source_repo_path" >&2
  exit 1
fi

source_repo_path="$(cd -P -- "$source_repo_path" && pwd -P)"
target_repo_path="$(cd -P -- "$target_repo_path" && pwd -P)"
agent_name="ai-efficiency-performance-auditor.agent.md"
source_agent="${source_repo_path}/.github/agents/${agent_name}"
target_agents_dir="${target_repo_path}/.github/agents"
target_agent="${target_agents_dir}/${agent_name}"
target_skills_root="${target_repo_path}/.github/skills"
command_file="${target_repo_path}/SCOUT-AUDIT-COMMAND.txt"

# Preflight every requested input and output before creating install paths.
check_directory "${source_repo_path}/.github"
check_directory "${source_repo_path}/.github/agents"
[[ -f "$source_agent" && ! -L "$source_agent" ]] ||
  fail "Agent definition must be a regular file in the source repo: $source_agent"
check_directory "${target_repo_path}/.github"
check_directory "$target_agents_dir"
check_new_path "$target_agent"
check_new_path "$command_file"

if [[ -n "${unique_skills[0]+x}" ]]; then
  check_directory "${source_repo_path}/.github/skills"
  check_directory "$target_skills_root"
  for skill_name in "${unique_skills[@]}"; do
    source_skill="${source_repo_path}/.github/skills/${skill_name}"
    check_directory "$source_skill"
    [[ -d "$source_skill" ]] || fail "Requested skill not found in source repo: $source_skill"
    unsafe_entry="$(find "$source_skill" ! -type d ! -type f -print -quit)"
    [[ -z "$unsafe_entry" ]] || fail "Skill contains a link or non-regular entry: $unsafe_entry"
    check_new_path "${target_skills_root}/${skill_name}"
  done
fi

compose_scout_command() {
  local audit_target="$1"
  local focus="$2"
  local recipient="$3"
  local include_teams="$4"
  if [[ -n "$recipient" ]]; then
    if [[ "$include_teams" -eq 1 ]]; then
      echo "Audit ${audit_target}; focus on ${focus}; send report to ${recipient} and teams; format words."
    else
      echo "Audit ${audit_target}; focus on ${focus}; send report to ${recipient}; format words."
    fi
  else
    echo "Audit ${audit_target}; focus on ${focus}; format words."
  fi
}

scout_command="$(compose_scout_command "$resolved_audit_target" "$audit_focus" "$audit_email_recipient" "$include_teams_notification")"
set -o noclobber
ensure_directory "$target_agents_dir"
cat -- "$source_agent" > "$target_agent"
echo "Copied agent definition to ${target_agents_dir}"
if [[ -n "${unique_skills[0]+x}" ]]; then
  ensure_directory "$target_skills_root"
  for skill_name in "${unique_skills[@]}"; do
    target_skill="${target_skills_root}/${skill_name}"
    mkdir -- "$target_skill"
    cp -R -- "${source_repo_path}/.github/skills/${skill_name}/." "$target_skill"
    echo "Copied skill: $skill_name"
  done
fi
printf '%s\n' "$scout_command" > "$command_file"
echo
echo "Bootstrap complete."
echo "Target repo: $target_repo_path"
echo "Scout command saved: $command_file"
echo
echo "Run this in Scout:"
echo "$scout_command"
