import type { Env, MethodId } from '../../types'
import type { AnyMethod } from '../method'
import { pocock } from './pocock'
import { pstack } from './pstack'

// The method switch lists these in order. A session starts on the first one
// whose skills are installed, or on FALLBACK when none are.
export const METHODS: AnyMethod[] = [pstack, pocock]

// The beginner's flow: the safer start for someone with nothing installed.
const FALLBACK: MethodId = 'pocock'

export const methodOf = (id: MethodId | null | undefined): AnyMethod => METHODS.find(m => m.id === id) ?? METHODS.find(m => m.id === FALLBACK)!

export const isMethod = (id: unknown): id is MethodId => METHODS.some(m => m.id === id)

export const detect = (e: Env): MethodId => METHODS.find(m => e.plugins.some(k => m.requires.plugins.some(p => k.startsWith(p))))?.id ?? FALLBACK
