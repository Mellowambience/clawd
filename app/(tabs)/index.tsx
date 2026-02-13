import { useState, useRef, useEffect } from "react";
import {
  ScrollView,
  Text,
  View,
  TextInput,
  Pressable,
  KeyboardAvoidingView,
  Platform,
  FlatList,
} from "react-native";
import * as Haptics from "expo-haptics";
import AsyncStorage from "@react-native-async-storage/async-storage";

import { ScreenContainer } from "@/components/screen-container";
import { IconSymbol } from "@/components/ui/icon-symbol";
import { useColors } from "@/hooks/use-colors";
import { sendToMistGateway } from "@/lib/mist-gateway-client";

interface Message {
  id: string;
  text: string;
  sender: "user" | "ai";
  timestamp: number;
}

const STORAGE_KEY = "@moltbot_messages";

export default function ChatScreen() {
  const colors = useColors();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const flatListRef = useRef<FlatList>(null);

  // Load messages from storage on mount
  useEffect(() => {
    loadMessages();
  }, []);

  // Save messages whenever they change
  useEffect(() => {
    saveMessages();
  }, [messages]);

  const loadMessages = async () => {
    try {
      const stored = await AsyncStorage.getItem(STORAGE_KEY);
      if (stored) {
        setMessages(JSON.parse(stored));
      } else {
        // Add welcome message if no messages exist
        const welcomeMessage: Message = {
          id: Date.now().toString(),
          text: "Hi! I'm moltbot, your personal AI assistant. How can I help you today?",
          sender: "ai",
          timestamp: Date.now(),
        };
        setMessages([welcomeMessage]);
      }
    } catch (error) {
      console.error("Failed to load messages:", error);
    }
  };

  const saveMessages = async () => {
    try {
      await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
    } catch (error) {
      console.error("Failed to save messages:", error);
    }
  };

  const handleSend = async () => {
    if (!inputText.trim() || isLoading) return;

    if (Platform.OS !== "web") {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputText.trim(),
      sender: "user",
      timestamp: Date.now(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputText("");
    setIsLoading(true);

    const result = await sendToMistGateway(userMessage.text);
    const replyText = result.ok ? result.text : "MIST is offline. I can't reach the gateway right now.";
    const aiMessage: Message = {
      id: (Date.now() + 1).toString(),
      text: replyText,
      sender: "ai",
      timestamp: Date.now(),
    };
    setMessages((prev) => [...prev, aiMessage]);
    setIsLoading(false);
  };

  const renderMessage = ({ item }: { item: Message }) => {
    const isUser = item.sender === "user";
    return (
      <View
        className={`mb-3 ${isUser ? "items-end" : "items-start"}`}
      >
        <View
          className={`max-w-[80%] rounded-2xl px-4 py-3 ${
            isUser
              ? "bg-primary rounded-br-sm"
              : "bg-surface rounded-bl-sm"
          }`}
        >
          <Text
            className={`text-base leading-relaxed ${
              isUser ? "text-white" : "text-foreground"
            }`}
          >
            {item.text}
          </Text>
        </View>
      </View>
    );
  };

  return (
    <ScreenContainer className="flex-1">
      <KeyboardAvoidingView
        behavior={Platform.OS === "ios" ? "padding" : "height"}
        className="flex-1"
        keyboardVerticalOffset={Platform.OS === "ios" ? 90 : 0}
      >
        {/* Header */}
        <View className="px-4 py-3 border-b border-border">
          <Text className="text-2xl font-bold text-foreground">moltbot</Text>
          <Text className="text-sm text-muted">Your AI Assistant</Text>
        </View>

        {/* Messages */}
        <FlatList
          ref={flatListRef}
          data={messages}
          renderItem={renderMessage}
          keyExtractor={(item) => item.id}
          contentContainerStyle={{ padding: 16 }}
          onContentSizeChange={() =>
            flatListRef.current?.scrollToEnd({ animated: true })
          }
          onLayout={() => flatListRef.current?.scrollToEnd({ animated: false })}
        />

        {/* Loading indicator */}
        {isLoading && (
          <View className="px-4 pb-2">
            <View className="bg-surface rounded-2xl rounded-bl-sm px-4 py-3 max-w-[80%]">
              <Text className="text-muted">Thinking...</Text>
            </View>
          </View>
        )}

        {/* Input */}
        <View className="px-4 py-3 border-t border-border">
          <View className="flex-row items-center gap-2">
            <TextInput
              className="flex-1 bg-surface rounded-full px-4 py-3 text-base text-foreground"
              placeholder="Type a message..."
              placeholderTextColor={colors.muted}
              value={inputText}
              onChangeText={setInputText}
              onSubmitEditing={handleSend}
              returnKeyType="send"
              multiline
              maxLength={500}
            />
            <Pressable
              onPress={handleSend}
              disabled={!inputText.trim() || isLoading}
              style={({ pressed }: { pressed: boolean }) => ({
                backgroundColor: colors.primary,
                width: 48,
                height: 48,
                borderRadius: 24,
                alignItems: "center",
                justifyContent: "center",
                opacity: !inputText.trim() || isLoading ? 0.5 : pressed ? 0.8 : 1,
              })}
            >
              <IconSymbol name="paperplane.fill" size={22} color="white" />
            </Pressable>
          </View>
        </View>
      </KeyboardAvoidingView>
    </ScreenContainer>
  );
}
