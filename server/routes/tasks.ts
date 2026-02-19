import { z } from "zod";
import { publicProcedure, router } from "../_core/trpc";

// ── In-memory task storage ───────────────────────────────────────────────────
// Mirrors the mobile app's AsyncStorage model. In production, swap for DB.
interface Task {
  id: string;
  title: string;
  completed: boolean;
  createdAt: number;
}

const userTasks = new Map<string, Task[]>();

function getOrCreateTaskList(userId: string): Task[] {
  if (!userTasks.has(userId)) userTasks.set(userId, []);
  return userTasks.get(userId)!;
}

// ── Task router ──────────────────────────────────────────────────────────────
export const taskRouter = router({
  /** List all tasks for the current session/user */
  list: publicProcedure
    .input(
      z.object({
        userId: z.string().default("default"),
        filter: z.enum(["all", "active", "completed"]).default("all"),
      }),
    )
    .query(({ input }) => {
      const tasks = getOrCreateTaskList(input.userId);
      const filtered = tasks.filter((t) => {
        if (input.filter === "active") return !t.completed;
        if (input.filter === "completed") return t.completed;
        return true;
      });
      return {
        tasks: filtered,
        total: tasks.length,
        active: tasks.filter((t) => !t.completed).length,
        completed: tasks.filter((t) => t.completed).length,
      };
    }),

  /** Create a new task */
  create: publicProcedure
    .input(
      z.object({
        userId: z.string().default("default"),
        title: z.string().min(1).max(500),
      }),
    )
    .mutation(({ input }) => {
      const tasks = getOrCreateTaskList(input.userId);
      const task: Task = {
        id: Date.now().toString(),
        title: input.title,
        completed: false,
        createdAt: Date.now(),
      };
      tasks.unshift(task);
      return task;
    }),

  /** Toggle task completion */
  toggle: publicProcedure
    .input(
      z.object({
        userId: z.string().default("default"),
        taskId: z.string(),
      }),
    )
    .mutation(({ input }) => {
      const tasks = getOrCreateTaskList(input.userId);
      const task = tasks.find((t) => t.id === input.taskId);
      if (!task) throw new Error("Task not found");
      task.completed = !task.completed;
      return task;
    }),

  /** Delete a task */
  delete: publicProcedure
    .input(
      z.object({
        userId: z.string().default("default"),
        taskId: z.string(),
      }),
    )
    .mutation(({ input }) => {
      const tasks = getOrCreateTaskList(input.userId);
      const idx = tasks.findIndex((t) => t.id === input.taskId);
      if (idx === -1) throw new Error("Task not found");
      tasks.splice(idx, 1);
      return { success: true, taskId: input.taskId };
    }),

  /** Bulk sync — replace all tasks (for initial sync from mobile AsyncStorage) */
  sync: publicProcedure
    .input(
      z.object({
        userId: z.string().default("default"),
        tasks: z.array(
          z.object({
            id: z.string(),
            title: z.string(),
            completed: z.boolean(),
            createdAt: z.number(),
          }),
        ),
      }),
    )
    .mutation(({ input }) => {
      userTasks.set(input.userId, input.tasks);
      return { success: true, count: input.tasks.length };
    }),
});
