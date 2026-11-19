# Evals

End-to-end cases for `claude plugin eval`. Each case builds a fixture (a git repo with commits on fixed dates, plus agent-session logs in the run's isolated home) and checks the report against what the fixture contains.

```sh
claude plugin eval . --scaffold --trust-plugin --ablation none \
  --allow-tools "Bash(git:*)" "Bash(python3:*)" "Bash(find:*)" "Bash(date:*)" "Bash(ls:*)"
```

- `--scaffold` is needed to build the fixtures. Read `scaffold.sh` before running it; it only creates files in the run's temporary workspace and home.
- `--allow-tools` grants the shell commands the skill uses. Without it the agent can't run `git`.
- Each run calls the model and costs money (about $0.25 per case per run). They are not part of CI.
- On macOS the eval sandbox can block `git` (xcrun can't write its cache). The skill then falls back to reading `.git/logs`, which still works for these fixtures. Linux runs `git` normally.

Regex graders check facts that must appear (ticket IDs, outcomes) or must never appear (em dashes). Anything that depends on context, such as "not reported as done" or "only mentioned as left out", goes to the LLM grader.
