"use server";

import { revalidatePath } from "next/cache";

import { removeSavedStory, saveStory } from "@/lib/api/client";

/**
 * Server Actions are the mutation boundary for saved stories — client
 * components (SaveStoryButton, RemoveSavedButton) call these directly.
 * They wrap the in-memory store in lib/api/client.ts and revalidate /saved
 * so it reflects the change on next render. See docs/PROJECT_STATE.md for
 * why this is in-memory rather than a real database.
 */

export async function saveStoryAction(articleId: string): Promise<void> {
  await saveStory(articleId);
  revalidatePath("/saved");
}

export async function removeSavedStoryAction(articleId: string): Promise<void> {
  await removeSavedStory(articleId);
  revalidatePath("/saved");
}
