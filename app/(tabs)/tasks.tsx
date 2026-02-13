import { useState, useEffect } from "react";
import {
  Text,
  View,
  FlatList,
  Pressable,
  TextInput,
  Modal,
  Platform,
} from "react-native";
import * as Haptics from "expo-haptics";
import AsyncStorage from "@react-native-async-storage/async-storage";

import { ScreenContainer } from "@/components/screen-container";
import { IconSymbol } from "@/components/ui/icon-symbol";
import { useColors } from "@/hooks/use-colors";

interface Task {
  id: string;
  title: string;
  completed: boolean;
  createdAt: number;
}

const STORAGE_KEY = "@moltbot_tasks";

export default function TasksScreen() {
  const colors = useColors();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newTaskTitle, setNewTaskTitle] = useState("");
  const [filter, setFilter] = useState<"all" | "active" | "completed">("all");

  useEffect(() => {
    loadTasks();
  }, []);

  useEffect(() => {
    saveTasks();
  }, [tasks]);

  const loadTasks = async () => {
    try {
      const stored = await AsyncStorage.getItem(STORAGE_KEY);
      if (stored) {
        setTasks(JSON.parse(stored));
      }
    } catch (error) {
      console.error("Failed to load tasks:", error);
    }
  };

  const saveTasks = async () => {
    try {
      await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
    } catch (error) {
      console.error("Failed to save tasks:", error);
    }
  };

  const addTask = () => {
    if (!newTaskTitle.trim()) return;

    if (Platform.OS !== "web") {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }

    const newTask: Task = {
      id: Date.now().toString(),
      title: newTaskTitle.trim(),
      completed: false,
      createdAt: Date.now(),
    };

    setTasks((prev) => [newTask, ...prev]);
    setNewTaskTitle("");
    setShowAddModal(false);
  };

  const toggleTask = (id: string) => {
    if (Platform.OS !== "web") {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    }

    setTasks((prev) =>
      prev.map((task) =>
        task.id === id ? { ...task, completed: !task.completed } : task
      )
    );
  };

  const deleteTask = (id: string) => {
    if (Platform.OS !== "web") {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }

    setTasks((prev) => prev.filter((task) => task.id !== id));
  };

  const filteredTasks = tasks.filter((task) => {
    if (filter === "active") return !task.completed;
    if (filter === "completed") return task.completed;
    return true;
  });

  const renderTask = ({ item }: { item: Task }) => (
    <View className="mb-3 bg-surface rounded-xl p-4 border border-border">
      <View className="flex-row items-center gap-3">
        <Pressable
          onPress={() => toggleTask(item.id)}
          style={({ pressed }) => ({
            width: 24,
            height: 24,
            borderRadius: 12,
            borderWidth: 2,
            borderColor: item.completed ? colors.primary : colors.border,
            backgroundColor: item.completed ? colors.primary : "transparent",
            alignItems: "center",
            justifyContent: "center",
            opacity: pressed ? 0.7 : 1,
          })}
        >
          {item.completed && (
            <Text className="text-white text-xs font-bold">✓</Text>
          )}
        </Pressable>

        <Text
          className={`flex-1 text-base ${
            item.completed ? "text-muted line-through" : "text-foreground"
          }`}
        >
          {item.title}
        </Text>

        <Pressable
          onPress={() => deleteTask(item.id)}
          style={({ pressed }) => ({
            padding: 4,
            opacity: pressed ? 0.5 : 0.7,
          })}
        >
          <Text className="text-error text-lg">×</Text>
        </Pressable>
      </View>
    </View>
  );

  return (
    <ScreenContainer className="flex-1">
      {/* Header */}
      <View className="px-4 py-3 border-b border-border">
        <Text className="text-2xl font-bold text-foreground">Tasks</Text>
        <Text className="text-sm text-muted">
          {tasks.filter((t) => !t.completed).length} active tasks
        </Text>
      </View>

      {/* Filter */}
      <View className="flex-row px-4 py-3 gap-2">
        {(["all", "active", "completed"] as const).map((f) => (
          <Pressable
            key={f}
            onPress={() => {
              if (Platform.OS !== "web") {
                Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
              }
              setFilter(f);
            }}
            style={({ pressed }) => ({
              paddingHorizontal: 16,
              paddingVertical: 8,
              borderRadius: 20,
              backgroundColor: filter === f ? colors.primary : colors.surface,
              opacity: pressed ? 0.7 : 1,
            })}
          >
            <Text
              className={`text-sm font-medium ${
                filter === f ? "text-white" : "text-foreground"
              }`}
            >
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </Text>
          </Pressable>
        ))}
      </View>

      {/* Task List */}
      <FlatList
        data={filteredTasks}
        renderItem={renderTask}
        keyExtractor={(item) => item.id}
        contentContainerStyle={{ padding: 16 }}
        ListEmptyComponent={
          <View className="items-center justify-center py-12">
            <Text className="text-muted text-base">No tasks yet</Text>
            <Text className="text-muted text-sm mt-2">
              Tap + to create your first task
            </Text>
          </View>
        }
      />

      {/* Add Button */}
      <View className="absolute bottom-6 right-6">
        <Pressable
          onPress={() => {
            if (Platform.OS !== "web") {
              Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
            }
            setShowAddModal(true);
          }}
          style={({ pressed }) => ({
            width: 56,
            height: 56,
            borderRadius: 28,
            backgroundColor: colors.primary,
            alignItems: "center",
            justifyContent: "center",
            shadowColor: "#000",
            shadowOffset: { width: 0, height: 2 },
            shadowOpacity: 0.25,
            shadowRadius: 4,
            elevation: 5,
            transform: [{ scale: pressed ? 0.95 : 1 }],
          })}
        >
          <Text className="text-white text-3xl font-light">+</Text>
        </Pressable>
      </View>

      {/* Add Task Modal */}
      <Modal
        visible={showAddModal}
        transparent
        animationType="fade"
        onRequestClose={() => setShowAddModal(false)}
      >
        <Pressable
          className="flex-1 bg-black/50 justify-center items-center"
          onPress={() => setShowAddModal(false)}
        >
          <Pressable
            className="bg-background rounded-2xl p-6 mx-6 w-full max-w-sm"
            onPress={(e) => e.stopPropagation()}
          >
            <Text className="text-xl font-bold text-foreground mb-4">
              New Task
            </Text>

            <TextInput
              className="bg-surface rounded-xl px-4 py-3 text-base text-foreground mb-4"
              placeholder="Task title..."
              placeholderTextColor={colors.muted}
              value={newTaskTitle}
              onChangeText={setNewTaskTitle}
              onSubmitEditing={addTask}
              returnKeyType="done"
              autoFocus
            />

            <View className="flex-row gap-3">
              <Pressable
                onPress={() => setShowAddModal(false)}
                style={({ pressed }) => ({
                  flex: 1,
                  paddingVertical: 12,
                  borderRadius: 12,
                  backgroundColor: colors.surface,
                  alignItems: "center",
                  opacity: pressed ? 0.7 : 1,
                })}
              >
                <Text className="text-foreground font-semibold">Cancel</Text>
              </Pressable>

              <Pressable
                onPress={addTask}
                disabled={!newTaskTitle.trim()}
                style={({ pressed }) => ({
                  flex: 1,
                  paddingVertical: 12,
                  borderRadius: 12,
                  backgroundColor: colors.primary,
                  alignItems: "center",
                  opacity: !newTaskTitle.trim() ? 0.5 : pressed ? 0.7 : 1,
                })}
              >
                <Text className="text-white font-semibold">Add Task</Text>
              </Pressable>
            </View>
          </Pressable>
        </Pressable>
      </Modal>
    </ScreenContainer>
  );
}
