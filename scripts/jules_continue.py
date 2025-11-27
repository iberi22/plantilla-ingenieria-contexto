#!/usr/bin/env python3
"""
Jules Task Continuation Script
Allows continuing Jules tasks by sending prompts for next phases via GitHub CLI
"""
import argparse
import subprocess
import sys
import json
import re


def get_jules_pr_info():
    """Get information about the most recent Jules PR"""
    try:
        # Get most recent Jules PR
        result = subprocess.run(
            ['gh', 'pr', 'list', '--author', 'google-labs-jules[bot]', '--json', 'number,title,body,url', '--limit', '1'],
            capture_output=True,
            text=True,
            check=True
        )

        prs = json.loads(result.stdout)
        if not prs:
            print("❌ No se encontraron PRs de Jules")
            return None

        pr = prs[0]

        # Extract task ID from PR body
        task_match = re.search(r'task\s+\[(\d+)\]', pr['body'])
        if task_match:
            pr['task_id'] = task_match.group(1)
            pr['task_url'] = f"https://jules.google.com/task/{pr['task_id']}"

        return pr
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al obtener información del PR: {e}")
        return None


def create_continuation_issue(pr_info, next_phase_prompt):
    """Create a GitHub issue for Jules to continue work"""
    try:
        task_id = pr_info.get('task_id', 'unknown')

        issue_body = f"""## 🔄 Continuación de Tarea Jules

**PR Anterior:** {pr_info['url']}
**Task ID:** {task_id}
**Fase Anterior:** {pr_info['title']}

---

### 📋 Siguiente Fase

{next_phase_prompt}

---

**Notas:**
- Esta issue fue creada automáticamente para continuar el trabajo de Jules
- El PR anterior ha sido completado y mergeado exitosamente
- Jules puede tomar esta issue y crear un nuevo PR para esta fase

@google-labs-jules Por favor continúa con esta fase de desarrollo.
"""

        # Create issue
        result = subprocess.run(
            ['gh', 'issue', 'create',
             '--title', f'Jules: Fase siguiente - {next_phase_prompt[:50]}...',
             '--body', issue_body,
             '--label', 'jules-task,enhancement'],
            capture_output=True,
            text=True,
            check=True
        )

        print("✅ Issue creada exitosamente!")
        print(result.stdout)
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Error al crear issue: {e}")
        return False


def comment_on_pr(pr_number, comment):
    """Add a comment to a PR"""
    try:
        result = subprocess.run(
            ['gh', 'pr', 'comment', str(pr_number), '--body', comment],
            capture_output=True,
            text=True,
            check=True
        )
        print("✅ Comentario añadido al PR!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al comentar en PR: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Continuar tareas de Jules con múltiples fases/PRs'
    )

    parser.add_argument(
        'action',
        choices=['status', 'continue', 'comment'],
        help='Acción a realizar'
    )

    parser.add_argument(
        '--prompt',
        help='Prompt para la siguiente fase (requerido con "continue")'
    )

    parser.add_argument(
        '--pr-number',
        type=int,
        help='Número del PR para comentar (requerido con "comment")'
    )

    parser.add_argument(
        '--message',
        help='Mensaje para comentar (requerido con "comment")'
    )

    args = parser.parse_args()

    # Get Jules PR info
    pr_info = get_jules_pr_info()
    if not pr_info:
        return 1

    if args.action == 'status':
        print("📊 Estado del último PR de Jules:\n")
        print(f"  🔢 PR #{pr_info['number']}")
        print(f"  📝 Título: {pr_info['title']}")
        print(f"  🔗 URL: {pr_info['url']}")
        if 'task_id' in pr_info:
            print(f"  🎯 Task ID: {pr_info['task_id']}")
            print(f"  📍 Task URL: {pr_info['task_url']}")
        return 0

    elif args.action == 'continue':
        if not args.prompt:
            print("❌ Error: --prompt es requerido para 'continue'")
            return 1

        print(f"\n🚀 Creando issue para continuar tarea Jules...")
        print(f"   PR anterior: #{pr_info['number']}")
        print(f"   Siguiente fase: {args.prompt[:80]}...\n")

        if create_continuation_issue(pr_info, args.prompt):
            return 0
        return 1

    elif args.action == 'comment':
        if not args.pr_number:
            print("❌ Error: --pr-number es requerido para 'comment'")
            return 1
        if not args.message:
            print("❌ Error: --message es requerido para 'comment'")
            return 1

        if comment_on_pr(args.pr_number, args.message):
            return 0
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
