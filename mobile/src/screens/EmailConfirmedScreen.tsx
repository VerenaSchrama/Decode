import React, { useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import { colors } from '../constants/colors';

interface EmailConfirmedScreenProps {
  onContinueToIntake: () => void;
  isLoading?: boolean;
}

export default function EmailConfirmedScreen({ 
  onContinueToIntake, 
  isLoading = false 
}: EmailConfirmedScreenProps) {
  
  useEffect(() => {
    // Auto-continue to intake after a short delay
    const timer = setTimeout(() => {
      if (!isLoading) {
        onContinueToIntake();
      }
    }, 2000);

    return () => clearTimeout(timer);
  }, [isLoading, onContinueToIntake]);

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        {/* Success Icon */}
        <View style={styles.iconContainer}>
          <Text style={styles.successIcon}>✅</Text>
        </View>

        {/* Title */}
        <Text style={styles.title}>Email Confirmed!</Text>
        
        {/* Description */}
        <Text style={styles.description}>
          Your email has been successfully verified. You can now continue with your health journey.
        </Text>

        {/* Loading or Continue Button */}
        {isLoading ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color={colors.primary} />
            <Text style={styles.loadingText}>Setting up your account...</Text>
          </View>
        ) : (
          <TouchableOpacity 
            style={styles.continueButton}
            onPress={onContinueToIntake}
          >
            <Text style={styles.continueButtonText}>Continue to Health Assessment</Text>
          </TouchableOpacity>
        )}

        {/* Auto-continue notice */}
        <Text style={styles.autoContinueText}>
          Automatically continuing in a moment...
        </Text>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 24,
  },
  iconContainer: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#10B981' + '20',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 24,
  },
  successIcon: {
    fontSize: 40,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: colors.primary,
    marginBottom: 16,
    textAlign: 'center',
  },
  description: {
    fontSize: 16,
    color: '#6B7280',
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: 32,
  },
  continueButton: {
    backgroundColor: colors.primary,
    paddingVertical: 16,
    paddingHorizontal: 24,
    borderRadius: 8,
    marginBottom: 16,
    alignItems: 'center',
    minWidth: 200,
  },
  continueButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  loadingContainer: {
    alignItems: 'center',
    marginBottom: 16,
  },
  loadingText: {
    marginTop: 12,
    fontSize: 16,
    color: '#6B7280',
  },
  autoContinueText: {
    fontSize: 14,
    color: '#9CA3AF',
    textAlign: 'center',
    fontStyle: 'italic',
  },
});
