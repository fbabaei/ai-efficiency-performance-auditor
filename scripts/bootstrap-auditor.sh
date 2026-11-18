#!/usr/bin/env bash
set -euo pipefail

target_repo_path=""
target_repo_url=""
source_repo_path=""
source_repo_url="https://github.com/fbabaei/ai-efficiency-performance-auditor.git"
source_url_provided=0
include_service_performance_skill=0
interactive=0
audit_focus="latency, token/tool-call efficiency, retries"
focus_provided=0
audit_email_recipient=""
recipient_provided=0
include_teams_notification=1
teams_preference_provided=0
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
  --interactive                 Choose an audit workflow and generate a Scout prompt
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
      source_repo_url="${2:-}"; source_url_provided=1; shift 2 ;;
    --skill)
      skills+=("${2:-}"); shift 2 ;;
    --include-service-performance-skill)
      include_service_performance_skill=1; shift ;;
    --interactive)
      interactive=1; shift ;;
    --audit-focus)
      audit_focus="${2:-}"; focus_provided=1; shift 2 ;;
    --audit-email-recipient)
      audit_email_recipient="${2:-}"; recipient_provided=1; shift 2 ;;
    --no-teams-notification)
      include_teams_notification=0; teams_preference_provided=1; shift ;;
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

read_prompt() {
  local value
  read -r -p "$1: " value || fail "Input ended before setup was complete."
  printf -v "$2" '%s' "${value%$'\r'}"
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
  script_dir="$(cd -P -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
  if [[ -z "$target_repo_path" && -z "$target_repo_url" ]]; then
    echo "Choose target mode:"
    echo "  1) GitHub repository URL"
    echo "  2) Local repository path"
    read_prompt "Enter 1 or 2" mode
    if [[ "$mode" == "1" ]]; then
      read_prompt "Target repository URL" target_repo_url
    elif [[ "$mode" == "2" ]]; then
      read_prompt "Target local repository path" target_repo_path
    else
      echo "Invalid selection. Enter 1 or 2." >&2
      exit 1
    fi
  fi

  workflow_ids=() workflow_titles=() workflow_skills=()
  echo "What would you like to do?"
  while IFS='|' read -r id title required; do
    required="${required%$'\r'}"
    workflow_ids+=("$id")
    workflow_titles+=("$title")
    workflow_skills+=("$required")
    printf '  %s) %s [%s]\n' "${#workflow_ids[@]}" "$title" "$id"
  done < "$script_dir/audit-workflows.txt"
  echo "  0) Cancel"
  selected=""
  while [[ -z "$selected" ]]; do
    read_prompt "Choose a number or workflow ID [1]" answer
    answer="${answer:-1}"
    if [[ "$answer" == 0 ]]; then
      echo "Setup cancelled."
      exit 0
    fi
    for i in "${!workflow_ids[@]}"; do
      if [[ "$answer" == "$((i + 1))" || "$answer" == "${workflow_ids[$i]}" ]]; then
        selected="$i"
        break
      fi
    done
    [[ -n "$selected" ]] || echo "Unknown workflow. Enter a listed number or ID."
  done
  title="${workflow_titles[$selected]}"
  required="${workflow_skills[$selected]}"
  workflow_prompt="$(awk -v heading="## $title" '
    { sub(/\r$/, "") }
    /^## / {
      if (section && opened) invalid = 1
      section = ($0 == heading)
      if (section) sections++
    }
    !section { next }
    opened && /^```[ \t]*$/ { opened = 0; next }
    !opened && /^```text$/ { opened = 1; blocks++; next }
    opened { print; if ($0 ~ /[^ \t]/) nonempty = 1 }
    END { if (sections != 1 || blocks != 1 || opened || invalid || !nonempty) exit 1 }
  ' "$script_dir/../docs/usage-prompts.md")" || fail "Expected one nonempty prompt for $title."
  if [[ -n "$required" ]]; then
    IFS=',' read -r -a required_skills < <(printf '%s\n' "$required")
    skills+=("${required_skills[@]}")
  fi
  printf 'Selected: %s. Required skills: %s.\n' "$title" "${required:-none}"
  if [[ "$focus_provided" -eq 0 ]]; then
    read_prompt "Additional focus within this workflow (optional)" audit_focus
  fi
  if [[ "$recipient_provided" -eq 0 ]]; then
    read_prompt "Email recipient for Scout delivery (optional)" audit_email_recipient
  fi
  if [[ -n "${audit_email_recipient//[[:space:]]/}" && "$teams_preference_provided" -eq 0 ]]; then
    include_teams_notification=0
    read_prompt "Include a Teams completion notification? (y/N)" answer
    case "$answer" in [yY]|[yY][eE][sS]) include_teams_notification=1 ;; esac
  fi
  if [[ -z "$source_repo_path" && "$source_url_provided" -eq 0 ]]; then
    source_repo_path="$(dirname -- "$script_dir")"
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

if [[ "$interactive" -eq 1 ]]; then
  scout_command="$(printf 'Use this local application repository (do not clone or update it): %s\nUse .github/agents/%s and any explicitly requested skill files as audit guidance. Do not broaden the selected evidence scope.\n\n%s' "$target_repo_path" "$agent_name" "$workflow_prompt")"
  if [[ -n "${audit_focus//[[:space:]]/}" ]]; then
    scout_command+=$'\n\n'"Additional focus within the selected scope: $audit_focus"
  fi
  if [[ -n "${audit_email_recipient//[[:space:]]/}" ]]; then
    scout_command+=$'\n\n'"Scout delivery only: After the audit, confirm the recipient and approved summary content with me before emailing $audit_email_recipient. Do not send source code or raw evidence."
    if [[ "$include_teams_notification" -eq 1 ]]; then
      scout_command+=" After successful email delivery, send the same recipient a brief Teams completion notification without audit details."
    fi
  fi
else
  scout_command="$(compose_scout_command "$resolved_audit_target" "$audit_focus" "$audit_email_recipient" "$include_teams_notification")"
fi
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
if [[ "$interactive" -eq 1 ]]; then
  echo "Review and replace placeholders before pasting into Scout:"
else
  echo "Run this in Scout:"
fi
echo "$scout_command"
