#!/usr/bin/env bash
set -euo pipefail

target_repo_path=""
target_repo_url=""
source_repo_path=""
source_repo_url="https://github.com/fbabaei/ai-efficiency-performance-auditor.git"
include_service_performance_skill=0
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
  -h, --help                    Show this help

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

ensure_directory() {
  mkdir -p "$1"
}

resolve_repo_name() {
  local url="$1"
  local trimmed="${url%/}"
  local name
  name="$(basename "$trimmed")"
  name="${name%.git}"
  if [[ -z "$name" ]]; then
    echo "Could not infer repository name from URL: $url" >&2
    exit 1
  fi
  echo "$name"
}

ensure_repo() {
  local local_path="$1"
  local repo_url="$2"
  if [[ -d "$local_path" ]]; then
    if [[ ! -d "$local_path/.git" ]]; then
      echo "Path exists but is not a git repository: $local_path" >&2
      exit 1
    fi
    echo "Updating repository: $local_path"
    git -C "$local_path" pull --ff-only
    return
  fi
  ensure_directory "$(dirname "$local_path")"
  echo "Cloning repository: $repo_url -> $local_path"
  git clone "$repo_url" "$local_path"
}

working_root="${HOME}/workspace"
ensure_directory "$working_root"

if [[ -z "$target_repo_path" && -z "$target_repo_url" ]]; then
  echo "Provide --target-repo-path or --target-repo-url." >&2
  exit 1
fi

if [[ -z "$target_repo_path" ]]; then
  target_name="$(resolve_repo_name "$target_repo_url")"
  target_repo_path="${working_root}/${target_name}"
  ensure_repo "$target_repo_path" "$target_repo_url"
elif [[ ! -d "$target_repo_path/.git" ]]; then
  echo "Target path is not a git repository: $target_repo_path" >&2
  exit 1
fi

if [[ -z "$source_repo_path" ]]; then
  source_name="$(resolve_repo_name "$source_repo_url")"
  source_repo_path="${working_root}/${source_name}"
  ensure_repo "$source_repo_path" "$source_repo_url"
elif [[ ! -d "$source_repo_path/.git" ]]; then
  echo "Source path is not a git repository: $source_repo_path" >&2
  exit 1
fi

source_agent="${source_repo_path}/.github/agents/ai-efficiency-performance-auditor.agent.md"
if [[ ! -f "$source_agent" ]]; then
  echo "Agent definition not found in source repo: $source_agent" >&2
  exit 1
fi

target_agents_dir="${target_repo_path}/.github/agents"
ensure_directory "$target_agents_dir"
cp -f "$source_agent" "${target_agents_dir}/ai-efficiency-performance-auditor.agent.md"
echo "Copied agent definition to ${target_agents_dir}"

if [[ "$include_service_performance_skill" -eq 1 ]]; then
  skills+=("service-performance-review")
fi

if [[ "${#skills[@]}" -gt 0 ]]; then
  mapfile -t unique_skills < <(printf '%s\n' "${skills[@]}" | sed '/^\s*$/d' | awk '!seen[$0]++')
  target_skills_root="${target_repo_path}/.github/skills"
  ensure_directory "$target_skills_root"
  for skill_name in "${unique_skills[@]}"; do
    source_skill="${source_repo_path}/.github/skills/${skill_name}"
    if [[ ! -d "$source_skill" ]]; then
      echo "Requested skill not found in source repo: $source_skill" >&2
      exit 1
    fi
    target_skill="${target_skills_root}/${skill_name}"
    rm -rf "$target_skill"
    cp -R "$source_skill" "$target_skill"
    echo "Copied skill: $skill_name"
  done
fi

echo
echo "Bootstrap complete."
echo "Target repo: $target_repo_path"
echo "Next step: open the target repo and run an audit prompt with AI Efficiency & Performance Auditor."
