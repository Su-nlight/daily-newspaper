import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";

afterEach(() => cleanup());

// jsdom doesn't implement scrolling; the chat auto-scrolls its log. (Guarded
// so tests that opt into the node environment still load this file.)
if (typeof Element !== "undefined") {
  Element.prototype.scrollTo = () => {};
}
