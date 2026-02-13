import { useState, useEffect } from "react";
import { Text, View, ScrollView, Pressable, Platform, Switch } from "react-native";
import * as Haptics from "expo-haptics";
import AsyncStorage from "@react-native-async-storage/async-storage";

import { ScreenContainer } from "@/components/screen-container";
import { useColors } from "@/hooks/use-colors";
import { useColorScheme } from "@/hooks/use-color-scheme";

const STORAGE_KEY = "@moltbot_settings";

interface Settings {
  notifications: boolean;
  haptics: boolean;
  aiModel: "gpt-4" | "claude" | "local";
}

export default function ProfileScreen() {
  const colors = useColors();
  const colorScheme = useColorScheme();
  const [settings, setSettings] = useState<Settings>({
    notifications: true,
    haptics: true,
    aiModel: "gpt-4",
  });

  useEffect(() => {
    loadSettings();
  }, []);

  useEffect(() => {
    saveSettings();
  }, [settings]);

  const loadSettings = async () => {
    try {
      const stored = await AsyncStorage.getItem(STORAGE_KEY);
      if (stored) {
        setSettings(JSON.parse(stored));
      }
    } catch (error) {
      console.error("Failed to load settings:", error);
    }
  };

  const saveSettings = async () => {
    try {
      await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
    } catch (error) {
      console.error("Failed to save settings:", error);
    }
  };

  const toggleSetting = (key: keyof Settings) => {
    if (Platform.OS !== "web") {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }
    setSettings((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  const selectAIModel = (model: Settings["aiModel"]) => {
    if (Platform.OS !== "web") {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    }
    setSettings((prev) => ({ ...prev, aiModel: model }));
  };

  return (
    <ScreenContainer className="flex-1">
      <ScrollView>
        {/* Header */}
        <View className="px-4 py-3 border-b border-border">
          <Text className="text-2xl font-bold text-foreground">Profile</Text>
          <Text className="text-sm text-muted">Settings & Preferences</Text>
        </View>

        {/* Profile Info */}
        <View className="p-4">
          <View className="bg-surface rounded-2xl p-6 items-center border border-border">
            <View
              style={{
                width: 80,
                height: 80,
                borderRadius: 40,
                backgroundColor: colors.primary,
                alignItems: "center",
                justifyContent: "center",
                marginBottom: 12,
              }}
            >
              <Text className="text-4xl">🦀</Text>
            </View>
            <Text className="text-xl font-bold text-foreground">moltbot</Text>
            <Text className="text-sm text-muted mt-1">Your AI Assistant</Text>
          </View>
        </View>

        {/* AI Model Selection */}
        <View className="px-4 pb-4">
          <Text className="text-base font-semibold text-foreground mb-3">
            AI Model
          </Text>
          <View className="gap-2">
            {(["gpt-4", "claude", "local"] as const).map((model) => (
              <Pressable
                key={model}
                onPress={() => selectAIModel(model)}
                style={({ pressed }) => ({
                  backgroundColor: colors.surface,
                  borderRadius: 12,
                  padding: 16,
                  borderWidth: 2,
                  borderColor:
                    settings.aiModel === model ? colors.primary : colors.border,
                  opacity: pressed ? 0.7 : 1,
                })}
              >
                <View className="flex-row items-center justify-between">
                  <View>
                    <Text className="text-base font-medium text-foreground">
                      {model === "gpt-4"
                        ? "GPT-4"
                        : model === "claude"
                        ? "Claude"
                        : "Local Model"}
                    </Text>
                    <Text className="text-sm text-muted mt-1">
                      {model === "gpt-4"
                        ? "OpenAI's most capable model"
                        : model === "claude"
                        ? "Anthropic's Claude AI"
                        : "Run AI locally on device"}
                    </Text>
                  </View>
                  {settings.aiModel === model && (
                    <View
                      style={{
                        width: 24,
                        height: 24,
                        borderRadius: 12,
                        backgroundColor: colors.primary,
                        alignItems: "center",
                        justifyContent: "center",
                      }}
                    >
                      <Text className="text-white text-xs font-bold">✓</Text>
                    </View>
                  )}
                </View>
              </Pressable>
            ))}
          </View>
        </View>

        {/* Settings */}
        <View className="px-4 pb-4">
          <Text className="text-base font-semibold text-foreground mb-3">
            Preferences
          </Text>

          <View className="bg-surface rounded-2xl border border-border overflow-hidden">
            <View className="px-4 py-4 flex-row items-center justify-between border-b border-border">
              <View className="flex-1">
                <Text className="text-base text-foreground">Notifications</Text>
                <Text className="text-sm text-muted mt-1">
                  Receive task and reminder alerts
                </Text>
              </View>
              <Switch
                value={settings.notifications}
                onValueChange={() => toggleSetting("notifications")}
                trackColor={{ false: colors.border, true: colors.primary }}
                thumbColor={colors.background}
              />
            </View>

            <View className="px-4 py-4 flex-row items-center justify-between">
              <View className="flex-1">
                <Text className="text-base text-foreground">Haptic Feedback</Text>
                <Text className="text-sm text-muted mt-1">
                  Vibrate on interactions
                </Text>
              </View>
              <Switch
                value={settings.haptics}
                onValueChange={() => toggleSetting("haptics")}
                trackColor={{ false: colors.border, true: colors.primary }}
                thumbColor={colors.background}
              />
            </View>
          </View>
        </View>

        {/* Theme Info */}
        <View className="px-4 pb-4">
          <Text className="text-base font-semibold text-foreground mb-3">
            Appearance
          </Text>
          <View className="bg-surface rounded-2xl p-4 border border-border">
            <View className="flex-row items-center justify-between">
              <Text className="text-base text-foreground">Theme</Text>
              <Text className="text-sm font-medium text-primary">
                {colorScheme === "dark" ? "Dark" : "Light"}
              </Text>
            </View>
            <Text className="text-sm text-muted mt-2">
              Theme follows your system settings
            </Text>
          </View>
        </View>

        {/* About */}
        <View className="px-4 pb-6">
          <Text className="text-base font-semibold text-foreground mb-3">
            About
          </Text>
          <View className="bg-surface rounded-2xl p-4 border border-border">
            <Text className="text-sm text-foreground leading-relaxed">
              moltbot is a personal AI assistant inspired by OpenClaw. It helps
              you manage tasks, connect services, and automate your daily
              activities.
            </Text>
            <Text className="text-xs text-muted mt-3">Version 1.0.0</Text>
          </View>
        </View>
      </ScrollView>
    </ScreenContainer>
  );
}
