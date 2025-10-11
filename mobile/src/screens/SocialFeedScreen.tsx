import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Modal,
  SafeAreaView,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors } from '../constants/colors';

interface Post {
  id: string;
  user: {
    name: string;
    avatar: string;
    isVerified: boolean;
  };
  content: string;
  type: 'habit_start' | 'intervention_complete' | 'milestone' | 'inspiration' | 'custom';
  intervention?: string;
  habits?: string[];
  likes: number;
  comments: number;
  timestamp: string;
  isLiked: boolean;
}

const dummyPosts: Post[] = [
  {
    id: '1',
    user: {
      name: 'Sarah M.',
      avatar: '👩‍⚕️',
      isVerified: true,
    },
    content: 'Just completed my first week of the "Blood Sugar Balance" intervention! Feeling more energetic and my cravings have decreased significantly. The morning protein habit has been a game-changer! 🎉',
    type: 'intervention_complete',
    intervention: 'Blood Sugar Balance',
    habits: ['Eat protein with breakfast', 'Walk after meals', 'Limit processed sugars'],
    likes: 24,
    comments: 8,
    timestamp: '2 hours ago',
    isLiked: false,
  },
  {
    id: '2',
    user: {
      name: 'Emma L.',
      avatar: '🌱',
      isVerified: false,
    },
    content: 'Starting my journey with cycle-aware nutrition today! Excited to see how tracking my cycle phases will help with my energy levels and mood. Any tips for a beginner? 💪',
    type: 'habit_start',
    intervention: 'Cycle-Aware Nutrition',
    habits: ['Track cycle phases', 'Eat with your cycle', 'Morning meditation'],
    likes: 18,
    comments: 12,
    timestamp: '4 hours ago',
    isLiked: true,
  },
  {
    id: '3',
    user: {
      name: 'Dr. Maria Rodriguez',
      avatar: '👩‍⚕️',
      isVerified: true,
    },
    content: 'Remember: Small, consistent changes lead to big transformations. You don\'t have to be perfect, just persistent. Every healthy choice counts! 🌟',
    type: 'inspiration',
    likes: 45,
    comments: 6,
    timestamp: '6 hours ago',
    isLiked: false,
  },
  {
    id: '4',
    user: {
      name: 'Jessica K.',
      avatar: '🌸',
      isVerified: false,
    },
    content: '30-day streak with my "Hormone Balance" habits! My PMS symptoms have been so much more manageable this month. The magnesium supplement and evening routine really made a difference.',
    type: 'milestone',
    intervention: 'Hormone Balance',
    habits: ['Evening magnesium', 'Stress management', 'Sleep hygiene'],
    likes: 32,
    comments: 15,
    timestamp: '1 day ago',
    isLiked: false,
  },
  {
    id: '5',
    user: {
      name: 'Alex T.',
      avatar: '💪',
      isVerified: false,
    },
    content: 'Just finished my first week of the "PCOS Management" intervention. The low-glycemic eating has been challenging but I\'m already feeling less bloated and more in control of my cravings.',
    type: 'intervention_complete',
    intervention: 'PCOS Management',
    habits: ['Low-glycemic meals', 'Regular exercise', 'Stress reduction'],
    likes: 28,
    comments: 9,
    timestamp: '1 day ago',
    isLiked: true,
  },
  {
    id: '6',
    user: {
      name: 'Community',
      avatar: '👥',
      isVerified: true,
    },
    content: 'Weekly reminder: You\'re not alone in this journey! 85% of women in our community report improved symptoms within 4 weeks of starting their intervention. Keep going! 💕',
    type: 'inspiration',
    likes: 67,
    comments: 23,
    timestamp: '2 days ago',
    isLiked: false,
  },
];

export default function SocialFeedScreen() {
  const [posts, setPosts] = useState<Post[]>(dummyPosts);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newPostContent, setNewPostContent] = useState('');

  const handleLike = (postId: string) => {
    setPosts(prevPosts =>
      prevPosts.map(post =>
        post.id === postId
          ? {
              ...post,
              isLiked: !post.isLiked,
              likes: post.isLiked ? post.likes - 1 : post.likes + 1,
            }
          : post
      )
    );
  };

  const handleCreatePost = () => {
    if (newPostContent.trim()) {
      const newPost: Post = {
        id: Date.now().toString(),
        user: {
          name: 'You',
          avatar: '👤',
          isVerified: false,
        },
        content: newPostContent.trim(),
        type: 'custom',
        likes: 0,
        comments: 0,
        timestamp: 'Just now',
        isLiked: false,
      };
      setPosts(prevPosts => [newPost, ...prevPosts]);
      setNewPostContent('');
      setShowCreateModal(false);
      Alert.alert('Success', 'Your post has been shared!');
    }
  };

  const getPostIcon = (type: string) => {
    switch (type) {
      case 'habit_start':
        return '🚀';
      case 'intervention_complete':
        return '🎉';
      case 'milestone':
        return '🏆';
      case 'inspiration':
        return '💡';
      default:
        return '📝';
    }
  };

  const getPostTypeText = (type: string) => {
    switch (type) {
      case 'habit_start':
        return 'Started New Habits';
      case 'intervention_complete':
        return 'Completed Intervention';
      case 'milestone':
        return 'Achievement';
      case 'inspiration':
        return 'Inspiration';
      default:
        return 'Personal Post';
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>Community Feed</Text>
          <Text style={styles.subtitle}>Connect and inspire each other</Text>
        </View>

        {/* Create Post Button */}
        <TouchableOpacity
          style={styles.createPostButton}
          onPress={() => setShowCreateModal(true)}
        >
          <Ionicons name="add-circle" size={24} color={colors.primary} />
          <Text style={styles.createPostText}>Share your progress</Text>
        </TouchableOpacity>

        {/* Posts */}
        {posts.map((post) => (
          <View key={post.id} style={styles.postCard}>
            {/* Post Header */}
            <View style={styles.postHeader}>
              <View style={styles.userInfo}>
                <Text style={styles.avatar}>{post.user.avatar}</Text>
                <View style={styles.userDetails}>
                  <View style={styles.userNameRow}>
                    <Text style={styles.userName}>{post.user.name}</Text>
                    {post.user.isVerified && (
                      <Ionicons name="checkmark-circle" size={16} color={colors.primary} />
                    )}
                  </View>
                  <View style={styles.postMeta}>
                    <Text style={styles.postType}>
                      {getPostIcon(post.type)} {getPostTypeText(post.type)}
                    </Text>
                    <Text style={styles.timestamp}>• {post.timestamp}</Text>
                  </View>
                </View>
              </View>
            </View>

            {/* Post Content */}
            <Text style={styles.postContent}>{post.content}</Text>

            {/* Intervention/Habits Info */}
            {post.intervention && (
              <View style={styles.interventionInfo}>
                <Text style={styles.interventionTitle}>Intervention: {post.intervention}</Text>
                {post.habits && (
                  <View style={styles.habitsList}>
                    {post.habits.map((habit, index) => (
                      <Text key={index} style={styles.habitItem}>• {habit}</Text>
                    ))}
                  </View>
                )}
              </View>
            )}

            {/* Post Actions */}
            <View style={styles.postActions}>
              <TouchableOpacity
                style={styles.actionButton}
                onPress={() => handleLike(post.id)}
              >
                <Ionicons
                  name={post.isLiked ? "heart" : "heart-outline"}
                  size={20}
                  color={post.isLiked ? colors.primary : colors.textSecondary}
                />
                <Text style={[
                  styles.actionText,
                  post.isLiked && styles.actionTextActive
                ]}>
                  {post.likes}
                </Text>
              </TouchableOpacity>
              
              <TouchableOpacity style={styles.actionButton}>
                <Ionicons name="chatbubble-outline" size={20} color={colors.textSecondary} />
                <Text style={styles.actionText}>{post.comments}</Text>
              </TouchableOpacity>
              
              <TouchableOpacity style={styles.actionButton}>
                <Ionicons name="share-outline" size={20} color={colors.textSecondary} />
                <Text style={styles.actionText}>Share</Text>
              </TouchableOpacity>
            </View>
          </View>
        ))}
      </ScrollView>

      {/* Create Post Modal */}
      <Modal
        visible={showCreateModal}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setShowCreateModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Share Your Progress</Text>
              <TouchableOpacity
                style={styles.closeButton}
                onPress={() => setShowCreateModal(false)}
              >
                <Ionicons name="close" size={24} color={colors.textSecondary} />
              </TouchableOpacity>
            </View>

            <View style={styles.modalBody}>
              <Text style={styles.inputLabel}>What would you like to share?</Text>
              <TextInput
                style={styles.textInput}
                value={newPostContent}
                onChangeText={setNewPostContent}
                placeholder="Share your progress, ask for advice, or inspire others..."
                multiline
                numberOfLines={6}
                textAlignVertical="top"
                placeholderTextColor={colors.textSecondary}
              />
            </View>

            <View style={styles.modalFooter}>
              <TouchableOpacity
                style={styles.cancelButton}
                onPress={() => setShowCreateModal(false)}
              >
                <Text style={styles.cancelButtonText}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[
                  styles.postButton,
                  !newPostContent.trim() && styles.postButtonDisabled
                ]}
                onPress={handleCreatePost}
                disabled={!newPostContent.trim()}
              >
                <Text style={styles.postButtonText}>Share</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  content: {
    flex: 1,
    paddingHorizontal: 16,
  },
  header: {
    paddingVertical: 20,
    alignItems: 'center',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#6B7280',
    textAlign: 'center',
  },
  createPostButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    paddingVertical: 16,
    paddingHorizontal: 20,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
    borderWidth: 1,
    borderColor: colors.primary,
  },
  createPostText: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.primary,
    marginLeft: 8,
  },
  postCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  postHeader: {
    marginBottom: 12,
  },
  userInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  avatar: {
    fontSize: 32,
    marginRight: 12,
  },
  userDetails: {
    flex: 1,
  },
  userNameRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  userName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
    marginRight: 6,
  },
  postMeta: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  postType: {
    fontSize: 12,
    color: colors.primary,
    fontWeight: '500',
    marginRight: 8,
  },
  timestamp: {
    fontSize: 12,
    color: '#9CA3AF',
  },
  postContent: {
    fontSize: 16,
    color: '#1F2937',
    lineHeight: 22,
    marginBottom: 12,
  },
  interventionInfo: {
    backgroundColor: '#F0F9FF',
    borderRadius: 8,
    padding: 12,
    marginBottom: 12,
    borderLeftWidth: 3,
    borderLeftColor: colors.primary,
  },
  interventionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.primary,
    marginBottom: 8,
  },
  habitsList: {
    marginLeft: 8,
  },
  habitItem: {
    fontSize: 13,
    color: '#6B7280',
    marginBottom: 2,
  },
  postActions: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#F3F4F6',
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 24,
  },
  actionText: {
    fontSize: 14,
    color: '#6B7280',
    marginLeft: 6,
  },
  actionTextActive: {
    color: colors.primary,
    fontWeight: '600',
  },
  // Modal styles
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: '#FFFFFF',
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    maxHeight: '80%',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#1F2937',
  },
  closeButton: {
    padding: 4,
  },
  modalBody: {
    paddingHorizontal: 20,
    paddingVertical: 20,
  },
  inputLabel: {
    fontSize: 16,
    fontWeight: '500',
    color: '#1F2937',
    marginBottom: 12,
  },
  textInput: {
    borderWidth: 1,
    borderColor: '#E5E7EB',
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 16,
    color: '#1F2937',
    backgroundColor: '#F9FAFB',
    minHeight: 120,
    textAlignVertical: 'top',
  },
  modalFooter: {
    flexDirection: 'row',
    paddingHorizontal: 20,
    paddingVertical: 16,
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
    gap: 12,
  },
  cancelButton: {
    flex: 1,
    paddingVertical: 14,
    backgroundColor: '#F3F4F6',
    borderRadius: 12,
    alignItems: 'center',
  },
  cancelButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#6B7280',
  },
  postButton: {
    flex: 1,
    paddingVertical: 14,
    backgroundColor: colors.primary,
    borderRadius: 12,
    alignItems: 'center',
  },
  postButtonDisabled: {
    backgroundColor: '#D1D5DB',
  },
  postButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFFFFF',
  },
});
