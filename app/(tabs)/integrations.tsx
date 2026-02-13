import { useState, useEffect } from "react";
import { Text, View, FlatList, Pressable, Platform } from "react-native";
import * as Haptics from "expo-haptics";
import AsyncStorage from "@react-native-async-storage/async-storage";

import { ScreenContainer } from "@/components/screen-container";
import { useColors } from "@/hooks/use-colors";

interface Integration {
  id: string;
  name: string;
  category: string;
  icon: string;
  connected: boolean;
  description: string;
}

const STORAGE_KEY = "@moltbot_integrations";

const DEFAULT_INTEGRATIONS: Integration[] = [
  {
    id: "calendar",
    name: "Calendar",
    category: "Productivity",
    icon: "📅",
    connected: false,
    description: "Manage your events and schedule",
  },
  {
    id: "email",
    name: "Email",
    category: "Communication",
    icon: "📧",
    connected: false,
    description: "Send and read emails",
  },
  {
    id: "reminders",
    name: "Reminders",
    category: "Productivity",
    icon: "⏰",
    connected: false,
    description: "Set and manage reminders",
  },
  {
    id: "notes",
    name: "Notes",
    category: "Productivity",
    icon: "📝",
    connected: false,
    description: "Create and organize notes",
  },
  {
    id: "weather",
    name: "Weather",
    category: "Information",
    icon: "🌤️",
    connected: false,
    description: "Get weather updates",
  },
  {
    id: "music",
    name: "Music",
    category: "Entertainment",
    icon: "🎵",
    connected: false,
    description: "Control music playback",
  },
  {
    id: "smart-home",
    name: "Smart Home",
    category: "IoT",
    icon: "🏠",
    connected: false,
    description: "Control smart home devices",
  },
  {
    id: "health",
    name: "Health",
    category: "Health",
    icon: "❤️",
    connected: false,
    description: "Track health metrics",
  },
];

export default function IntegrationsScreen() {
  const colors = useColors();
  const [integrations, setIntegrations] = useState<Integration[]>(DEFAULT_INTEGRATIONS);

  useEffect(() => {
    loadIntegrations();
  }, []);

  useEffect(() => {
    saveIntegrations();
  }, [integrations]);

  const loadIntegrations = async () => {
    try {
      const stored = await AsyncStorage.getItem(STORAGE_KEY);
      if (stored) {
        setIntegrations(JSON.parse(stored));
      }
    } catch (error) {
      console.error("Failed to load integrations:", error);
    }
  };

  const saveIntegrations = async () => {
    try {
      await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(integrations));
    } catch (error) {
      console.error("Failed to save integrations:", error);
    }
  };

  const toggleIntegration = (id: string) => {
    if (Platform.OS !== "web") {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    }

    setIntegrations((prev) =>
      prev.map((integration) =>
        integration.id === id
          ? { ...integration, connected: !integration.connected }
          : integration
      )
    );
  };

  const renderIntegration = ({ item }: { item: Integration }) => (
    <View className="mb-3">
      <Pressable
        onPress={() => toggleIntegration(item.id)}
        style={({ pressed }) => ({
          backgroundColor: colors.surface,
          borderRadius: 16,
          padding: 16,
          borderWidth: 1,
          borderColor: item.connected ? colors.primary : colors.border,
          opacity: pressed ? 0.7 : 1,
        })}
      >
        <View className="flex-row items-center gap-3">
          <View
            style={{
              width: 48,
              height: 48,
              borderRadius: 24,
              backgroundColor: colors.background,
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <Text className="text-2xl">{item.icon}</Text>
          </View>

          <View className="flex-1">
            <Text className="text-base font-semibold text-foreground">
              {item.name}
            </Text>
            <Text className="text-sm text-muted">{item.description}</Text>
          </View>

          <View
            style={{
              width: 20,
              height: 20,
              borderRadius: 10,
              backgroundColor: item.connected ? colors.success : colors.border,
            }}
          />
        </View>

        {item.connected && (
          <View className="mt-3 pt-3 border-t border-border">
            <Text className="text-xs text-success font-medium">
              ✓ Connected
            </Text>
          </View>
        )}
      </Pressable>
    </View>
  );

  const connectedCount = integrations.filter((i) => i.connected).length;

  return (
    <ScreenContainer className="flex-1">
      {/* Header */}
      <View className="px-4 py-3 border-b border-border">
        <Text className="text-2xl font-bold text-foreground">Integrations</Text>
        <Text className="text-sm text-muted">
          {connectedCount} of {integrations.length} connected
        </Text>
      </View>

      {/* Info Banner */}
      <View className="mx-4 mt-4 bg-accent/10 rounded-xl p-4 border border-accent/20">
        <Text className="text-sm text-foreground leading-relaxed">
          Connect services to let moltbot help you with tasks, reminders, and more.
          Tap any integration to toggle its connection.
        </Text>
      </View>

      {/* Integrations List */}
      <FlatList
        data={integrations}
        renderItem={renderIntegration}
        keyExtractor={(item) => item.id}
        contentContainerStyle={{ padding: 16 }}
      />
    </ScreenContainer>
  );
}
