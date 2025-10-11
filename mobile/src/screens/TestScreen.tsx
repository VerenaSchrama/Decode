import React, { useState, useEffect } from 'react';
import { View, Text, Button, StyleSheet, ScrollView } from 'react-native';
import { checkAPIHealth, getRecommendations } from '../services/api';

export default function TestScreen() {
  const [status, setStatus] = useState('Testing API connection...');
  const [healthData, setHealthData] = useState<any>(null);
  const [recommendationData, setRecommendationData] = useState<any>(null);

  const testAPI = async () => {
    setStatus('Testing API connection...');
    const result = await checkAPIHealth();
    
    if (result.success) {
      setStatus('✅ API Connected Successfully!');
      setHealthData(result.data);
    } else {
      setStatus(`❌ API Error: ${result.error}`);
    }
  };

  const testRecommendation = async () => {
    setStatus('Testing recommendation endpoint...');
    
    const sampleInput = {
      profile: {
        name: "Test User",
        age: 28
      },
      symptoms: {
        selected: ["PCOS", "Weight gain"],
        additional: "Testing mobile app"
      },
      interventions: {
        selected: [],
        additional: "Testing custom intervention"
      },
      habits: {
        selected: [],
        additional: "Testing habit tracking"
      },
      dietaryPreferences: {
        selected: ["Mediterranean"],
        additional: "Testing dietary preferences"
      },
      consent: true,
      anonymous: false
    };

    const result = await getRecommendations(sampleInput);
    
    if (result.success) {
      setStatus('✅ Recommendation test successful!');
      setRecommendationData(result.data);
    } else {
      setStatus(`❌ Recommendation Error: ${result.error}`);
    }
  };

  useEffect(() => {
    testAPI();
  }, []);

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>HerFoodCode API Test</Text>
      
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>API Status</Text>
        <Text style={styles.status}>{status}</Text>
        <Button title="Test API Again" onPress={testAPI} />
      </View>

      {healthData && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Health Data</Text>
          <Text style={styles.dataText}>
            Status: {healthData.status}
          </Text>
          <Text style={styles.dataText}>
            RAG Pipeline: {healthData.rag_pipeline}
          </Text>
          <Text style={styles.dataText}>
            OpenAI API: {healthData.openai_api_key}
          </Text>
        </View>
      )}

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Test Recommendation</Text>
        <Button title="Test Recommendation" onPress={testRecommendation} />
      </View>

      {recommendationData && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Recommendation Result</Text>
          <Text style={styles.dataText}>
            Intervention: {recommendationData.recommended_intervention}
          </Text>
          <Text style={styles.dataText}>
            Similarity Score: {recommendationData.similarity_score}
          </Text>
          <Text style={styles.dataText}>
            Habits: {recommendationData.habits?.length || 0} recommended
          </Text>
          {recommendationData.data_collection && (
            <Text style={styles.dataText}>
              Data Collection: {recommendationData.data_collection.message}
            </Text>
          )}
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#f5f5f5',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 30,
    color: '#333',
  },
  section: {
    backgroundColor: 'white',
    padding: 15,
    marginBottom: 15,
    borderRadius: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#333',
  },
  status: {
    fontSize: 16,
    marginBottom: 10,
    color: '#666',
  },
  dataText: {
    fontSize: 14,
    marginBottom: 5,
    color: '#555',
  },
});

