import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  TextInput,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
  TouchableWithoutFeedback,
  Keyboard,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { colors } from '../constants/colors';
import { apiService, ChatMessage } from '../services/apiService';
import { useToast } from '../contexts/ToastContext';
import { useAuth } from '../contexts/AuthContext';

interface NutritionistChatScreenProps {
  intakeData?: any;
  currentIntervention?: any;
  selectedHabits?: string[];
  onBack: () => void;
}

export default function NutritionistChatScreen({
  intakeData,
  currentIntervention,
  selectedHabits,
  onBack,
}: NutritionistChatScreenProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);
  const scrollViewRef = useRef<ScrollView>(null);
  const inputRef = useRef<TextInput>(null);
  const { showToast } = useToast();
  const { user, session } = useAuth();

  // Use authenticated user ID and session
  const userId = user?.id;
  if (!userId || !session?.access_token) {
    console.error('No authenticated user or session found');
    return null;
  }

  // Set auth token for API service
  useEffect(() => {
    apiService.setAuthToken(session.access_token);
  }, [session?.access_token]);

  useEffect(() => {
    loadChatHistory();
  }, []);

  const loadChatHistory = async () => {
    try {
      setIsLoadingHistory(true);
      
      // Try to load from server first
      try {
        const data = await apiService.getChatHistory();
        
        if (data.messages && data.messages.length > 0) {
          // Reverse to show oldest first
          setMessages([...data.messages].reverse());
          console.log('Loaded chat history from server:', data.messages.length, 'messages');
          return;
        }
      } catch (serverError) {
        console.log('Server chat history not available, trying local storage');
      }
      
      // Fallback to local storage
      try {
        const localHistory = await AsyncStorage.getItem(`chat_history_${userId}`);
        if (localHistory) {
          const messages = JSON.parse(localHistory);
          setMessages(messages);
          console.log('Loaded chat history from local storage:', messages.length, 'messages');
        }
      } catch (localError) {
        console.log('No local chat history found');
      }
      
    } catch (error) {
      console.error('Error loading chat history:', error);
      showToast('Failed to load chat history', 'error');
    } finally {
      setIsLoadingHistory(false);
    }
  };

  const sendMessage = async () => {
    if (!inputText.trim() || isLoading) return;

    const messageText = inputText.trim();
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      user_id: userId,
      message: messageText,
      is_user: true,
      timestamp: new Date().toISOString(),
    };

    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    saveMessagesToLocalStorage(newMessages);
    setInputText('');
    // Keep focus after sending
    setTimeout(() => inputRef.current?.focus(), 0);
    setIsLoading(true);

    // Debug: Log what data we're sending
    console.log('=== CHAT DEBUG ===');
    console.log('intakeData:', intakeData);
    console.log('currentIntervention:', currentIntervention);
    console.log('selectedHabits:', selectedHabits);
    console.log('Sending to chat API:', {
      user_id: userId,
      message: messageText,
      intake_data: intakeData,
      current_intervention: currentIntervention,
      selected_habits: selectedHabits,
    });
    console.log('=== END DEBUG ===');

    try {
      // Prepare placeholder AI message we will append to incrementally
      const aiMessageId = (Date.now() + 1).toString();
      const startTimestamp = new Date().toISOString();
      const baseAiMessage: ChatMessage = {
        id: aiMessageId,
        user_id: userId,
        message: '',
        is_user: false,
        timestamp: startTimestamp,
      };

      setMessages(prev => {
        const updated = [...prev, baseAiMessage];
        saveMessagesToLocalStorage(updated);
        return updated;
      });

      // Helper to merge streamed chunks with light punctuation normalization
      const mergeChunk = (prev: string, chunk: string) => {
        let c = chunk;
        // If previous ends with a letter/number and chunk starts with space+lowercase, drop that space
        if (prev && /[A-Za-z0-9]$/.test(prev) && /^\s[a-z]/.test(c)) {
          c = c.replace(/^\s/, '');
        }
        let out = prev + c;
        // Remove spaces before punctuation
        out = out.replace(/\s+([,.;:!?])/g, '$1');
        // Fix spaces before apostrophes: it 's -> it's
        out = out.replace(/(\w)\s+'(\w)/g, "$1'$2");
        // Collapse multiple spaces
        out = out.replace(/ {2,}/g, ' ');
        return out;
      };

      await apiService.sendChatMessageStream(
        {
          user_id: userId,
          message: messageText,
          intake_data: intakeData,
          current_intervention: currentIntervention,
          selected_habits: selectedHabits,
        },
        (chunk) => {
          // Append streamed chunk to the last AI message
          setMessages(prev => {
            const updated = [...prev];
            const idx = updated.findIndex(m => m.id === aiMessageId);
            if (idx !== -1) {
              const prevText = updated[idx].message || '';
              const nextText = mergeChunk(prevText, chunk);
              updated[idx] = { ...updated[idx], message: nextText };
            }
            saveMessagesToLocalStorage(updated);
            return updated;
          });
        }
      );
    } catch (error) {
      console.error('Error sending message:', error);
      showToast(error instanceof Error ? error.message : 'Failed to send message. Please try again.', 'error');
      
      // Add error message to chat
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        user_id: userId,
        message: `Sorry, I encountered an error: ${error instanceof Error ? error.message : 'Unknown error'}. Please try again.`,
        is_user: false,
        timestamp: new Date().toISOString(),
      };
      setMessages(prevMessages => {
        const updatedMessages = [...prevMessages, errorMessage];
        saveMessagesToLocalStorage(updatedMessages);
        return updatedMessages;
      });
    } finally {
      setIsLoading(false);
    }
  };

  const saveMessagesToLocalStorage = async (messages: ChatMessage[]) => {
    try {
      await AsyncStorage.setItem(`chat_history_${userId}`, JSON.stringify(messages));
      console.log('Saved chat history to local storage:', messages.length, 'messages');
    } catch (error) {
      console.error('Error saving chat history to local storage:', error);
    }
  };

  const scrollToBottom = () => {
    scrollViewRef.current?.scrollToEnd({ animated: true });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  if (isLoadingHistory) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.header}>
          <TouchableOpacity style={styles.backButton} onPress={onBack}>
            <Text style={styles.backButtonText}>← Back</Text>
          </TouchableOpacity>
          <Text style={styles.title}>Nutritionist Chat</Text>
        </View>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={colors.primary} />
          <Text style={styles.loadingText}>Loading chat history...</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView 
        style={styles.keyboardAvoidingView}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
      >
          <View style={styles.keyboardDismissView}>
            {/* Header */}
            <View style={styles.header}>
          <TouchableOpacity style={styles.backButton} onPress={onBack}>
            <Text style={styles.backButtonText}>← Back</Text>
          </TouchableOpacity>
          <Text style={styles.title}>Nutritionist Chat</Text>
          <View style={styles.placeholder} />
        </View>

        {/* Messages (tap background to dismiss) */}
        <TouchableWithoutFeedback onPress={Keyboard.dismiss}>
          <View style={{ flex: 1 }}>
            <ScrollView 
              ref={scrollViewRef}
              style={styles.messagesContainer}
              contentContainerStyle={styles.messagesContent}
              showsVerticalScrollIndicator={false}
              keyboardShouldPersistTaps="handled"
              onScrollBeginDrag={Keyboard.dismiss}
            >
          {messages.length === 0 ? (
            <View style={styles.welcomeContainer}>
              <Text style={styles.welcomeTitle}>👋 Hi! I'm your AI Nutritionist</Text>
              <Text style={styles.welcomeText}>
                I'm here to help you with personalized nutrition advice based on your profile, 
                current intervention, and the latest scientific research.
              </Text>
              <Text style={styles.welcomeSubtext}>
                Ask me anything about your health journey!
              </Text>
            </View>
          ) : (
            messages.map((message) => (
              <View
                key={message.id}
                style={[
                  styles.messageContainer,
                  message.is_user ? styles.userMessageContainer : styles.aiMessageContainer,
                ]}
              >
                <View
                  style={[
                    styles.messageBubble,
                    message.is_user ? styles.userMessageBubble : styles.aiMessageBubble,
                  ]}
                >
                  <Text
                    style={[
                      styles.messageText,
                      message.is_user ? styles.userMessageText : styles.aiMessageText,
                    ]}
                  >
                    {message.message}
                  </Text>
                  <Text
                    style={[
                      styles.messageTime,
                      message.is_user ? styles.userMessageTime : styles.aiMessageTime,
                    ]}
                  >
                    {formatTime(message.timestamp)}
                  </Text>
                </View>
              </View>
            ))
          )}
          
          {isLoading && (
            <View style={styles.loadingMessageContainer}>
              <View style={styles.loadingMessageBubble}>
                <ActivityIndicator size="small" color={colors.primary} />
                <Text style={styles.loadingMessageText}>Nutritionist is typing...</Text>
              </View>
            </View>
          )}
            </ScrollView>
          </View>
        </TouchableWithoutFeedback>

        {/* Input */}
        <View style={styles.inputContainer} pointerEvents="box-none">
          <TextInput
            style={styles.textInput}
            ref={inputRef}
            value={inputText}
            onChangeText={setInputText}
            placeholder="Ask your nutritionist anything..."
            placeholderTextColor="#9ca3af"
            multiline
            maxLength={500}
            returnKeyType="send"
            onSubmitEditing={sendMessage}
            blurOnSubmit={false}
          />
          <TouchableOpacity
            style={[
              styles.sendButton,
              (!inputText.trim() || isLoading) && styles.sendButtonDisabled,
            ]}
            onPress={sendMessage}
            disabled={!inputText.trim() || isLoading}
          >
            <Text style={[
              styles.sendButtonText,
              (!inputText.trim() || isLoading) && styles.sendButtonTextDisabled,
            ]}>
              Send
            </Text>
          </TouchableOpacity>
        </View>
          </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  keyboardAvoidingView: {
    flex: 1,
  },
  keyboardDismissView: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 16,
    backgroundColor: '#ffffff',
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  backButton: {
    padding: 8,
  },
  backButtonText: {
    fontSize: 16,
    color: colors.primary,
    fontWeight: '500',
  },
  title: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1f2937',
  },
  placeholder: {
    width: 60, // Same width as back button for centering
  },
  messagesContainer: {
    flex: 1,
  },
  messagesContent: {
    padding: 16,
    paddingBottom: 8,
  },
  welcomeContainer: {
    alignItems: 'center',
    paddingVertical: 40,
    paddingHorizontal: 20,
  },
  welcomeTitle: {
    fontSize: 24,
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: 12,
    textAlign: 'center',
  },
  welcomeText: {
    fontSize: 16,
    color: '#6b7280',
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: 8,
  },
  welcomeSubtext: {
    fontSize: 14,
    color: colors.primary,
    fontWeight: '500',
    textAlign: 'center',
  },
  messageContainer: {
    marginBottom: 16,
  },
  userMessageContainer: {
    alignItems: 'flex-end',
  },
  aiMessageContainer: {
    alignItems: 'flex-start',
  },
  messageBubble: {
    maxWidth: '80%',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 20,
  },
  userMessageBubble: {
    backgroundColor: colors.primary,
    borderBottomRightRadius: 4,
  },
  aiMessageBubble: {
    backgroundColor: '#ffffff',
    borderWidth: 1,
    borderColor: '#e5e7eb',
    borderBottomLeftRadius: 4,
  },
  messageText: {
    fontSize: 16,
    lineHeight: 22,
  },
  userMessageText: {
    color: '#ffffff',
  },
  aiMessageText: {
    color: '#1f2937',
  },
  messageTime: {
    fontSize: 12,
    marginTop: 4,
  },
  userMessageTime: {
    color: '#e5e7eb',
  },
  aiMessageTime: {
    color: '#9ca3af',
  },
  loadingMessageContainer: {
    alignItems: 'flex-start',
    marginBottom: 16,
  },
  loadingMessageBubble: {
    backgroundColor: '#ffffff',
    borderWidth: 1,
    borderColor: '#e5e7eb',
    borderRadius: 20,
    borderBottomLeftRadius: 4,
    paddingHorizontal: 16,
    paddingVertical: 12,
    flexDirection: 'row',
    alignItems: 'center',
  },
  loadingMessageText: {
    fontSize: 14,
    color: '#6b7280',
    marginLeft: 8,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#ffffff',
    borderTopWidth: 1,
    borderTopColor: '#e5e7eb',
  },
  textInput: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#e5e7eb',
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 16,
    maxHeight: 100,
    marginRight: 12,
    backgroundColor: '#f9fafb',
  },
  sendButton: {
    backgroundColor: colors.primary,
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 20,
  },
  sendButtonDisabled: {
    backgroundColor: '#e5e7eb',
  },
  sendButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
  sendButtonTextDisabled: {
    color: '#9ca3af',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 12,
    fontSize: 16,
    color: '#6b7280',
  },
});
