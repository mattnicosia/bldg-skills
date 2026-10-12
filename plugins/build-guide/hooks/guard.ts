// Guard rail: no destructive git. Checked before a Bash call runs.

export type Blocked = { what: string; why: string } | null

const MAIN = /^(refs\/heads\/)?(main|master)$/

// One shell segment, tokens after `git` (global -C and -c options dropped).
const gitArgs = (segment: string) => {
  const words = segment.trim().split(/\s+/).filter(Boolean)
  const at = words.findIndex(w => w === 'git')
  if (at < 0 || words.slice(0, at).some(w => !/^(sudo|command|env|\w+=\S*)$/.test(w))) return null
  const rest = words.slice(at + 1)
  while (rest[0] === '-C' || rest[0] === '-c') rest.splice(0, 2)
  return rest
}

const pushBlock = (args: string[], branch: string): Blocked => {
  const flags = args.filter(a => a.startsWith('-'))
  const [, ...refspecs] = args.filter(a => !a.startsWith('-'))
  if (flags.some(f => f === '-f' || f === '--force' || f.startsWith('--force-with-lease') || (/^-[a-z]+$/.test(f) && f.includes('f'))) || refspecs.some(r => r.startsWith('+'))) {
    return { what: 'git push --force', why: 'A force push overwrites work on GitHub that may not exist anywhere else.' }
  }
  if (flags.includes('--all') || flags.includes('--mirror')) return { what: 'git push --all', why: 'It pushes every branch, main included.' }
  const targets = refspecs.length ? refspecs.map(r => (r.includes(':') ? r.split(':').pop() ?? '' : r === 'HEAD' ? branch : r)) : [branch]
  if (targets.some(t => MAIN.test(t))) return { what: 'git push to main', why: 'Main is the shared code. Changes reach it through a reviewed pull request.' }
  return null
}

const gitBlock = (args: string[], branch: string): Blocked => {
  const [verb = '', ...rest] = args
  const flags = rest.filter(a => a.startsWith('-'))
  const paths = rest.filter(a => !a.startsWith('-'))
  if (verb === 'push') return pushBlock(rest, branch)
  if (verb === 'reset' && flags.includes('--hard')) return { what: 'git reset --hard', why: 'It throws away every uncommitted change with no undo.' }
  if (verb === 'clean' && flags.some(f => f === '--force' || /^-[a-zA-Z]*f/.test(f))) return { what: 'git clean -f', why: 'It deletes files git does not track, with no undo.' }
  if (verb === 'branch' && (flags.includes('-D') || ((flags.includes('-d') || flags.includes('--delete')) && (flags.includes('-f') || flags.includes('--force'))))) {
    return { what: 'git branch -D', why: 'It deletes a branch even when its work was never merged.' }
  }
  if (verb === 'checkout' && paths.includes('.')) return { what: 'git checkout .', why: 'It throws away every uncommitted change with no undo.' }
  if (verb === 'restore' && paths.includes('.') && !(flags.includes('--staged') && !flags.includes('--worktree') && !flags.includes('-W'))) {
    return { what: 'git restore .', why: 'It throws away every uncommitted change with no undo.' }
  }
  return null
}

// Checks every segment of a shell command. `branch` is the current branch, for a
// bare `git push`; it is only read when a segment needs it.
export const guardBlock = async (command: string, branch: () => Promise<string>): Promise<Blocked> => {
  for (const segment of command.split(/&&|\|\||;|\||\n/)) {
    if (/^\s*gh\s+pr\s+merge\b/.test(segment)) return { what: 'gh pr merge', why: 'Merging adds the change to main. The person who reviews your work merges it.' }
    const args = gitArgs(segment)
    if (!args) continue
    const found = gitBlock(args, args[0] === 'push' ? await branch() : '')
    if (found) return found
  }
  return null
}
