// API service for MedStudy Pro integration with FastAPI backend

const API_BASE = 'http://localhost:8000/api';

export interface StudyPlan {
  id?: string;
  title: string;
  specialty: string;
  duration: number;
  difficulty: string;
  description?: string;
  focusAreas: string[];
  progress?: number;
  studyTime?: string;
  createdAt?: string;
}

export interface StudySession {
  id?: string;
  planId: string;
  duration: number;
  progress: number;
  confidence: number;
  completedAt?: string;
}

export interface AnalyticsData {
  totalStudyTime: number;
  activePlans: number;
  averageConfidence: number;
  currentStreak: number;
}

class APIService {
  private async fetchAPI(endpoint: string, options: RequestInit = {}) {
    const url = `${API_BASE}${endpoint}`;
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  // Health check
  async healthCheck() {
    return this.fetchAPI('/health');
  }

  // Study Plans
  async getPlans(): Promise<StudyPlan[]> {
    return this.fetchAPI('/plans');
  }

  async createPlan(planData: Omit<StudyPlan, 'id'>): Promise<StudyPlan> {
    return this.fetchAPI('/plans', {
      method: 'POST',
      body: JSON.stringify(planData),
    });
  }

  async getPlan(id: string): Promise<StudyPlan> {
    return this.fetchAPI(`/plans/${id}`);
  }

  async updatePlan(id: string, planData: Partial<StudyPlan>): Promise<StudyPlan> {
    return this.fetchAPI(`/plans/${id}`, {
      method: 'PUT',
      body: JSON.stringify(planData),
    });
  }

  async deletePlan(id: string): Promise<void> {
    return this.fetchAPI(`/plans/${id}`, {
      method: 'DELETE',
    });
  }

  // Study Sessions
  async startStudySession(planId: string): Promise<StudySession> {
    return this.fetchAPI('/study/start', {
      method: 'POST',
      body: JSON.stringify({ plan_id: planId }),
    });
  }

  async updateStudyProgress(sessionId: string, progress: number, confidence: number): Promise<StudySession> {
    return this.fetchAPI('/study/progress', {
      method: 'PUT',
      body: JSON.stringify({ 
        session_id: sessionId, 
        progress, 
        confidence 
      }),
    });
  }

  async completeStudySession(sessionId: string): Promise<StudySession> {
    return this.fetchAPI('/study/complete', {
      method: 'POST',
      body: JSON.stringify({ session_id: sessionId }),
    });
  }

  // Analytics
  async getAnalytics(): Promise<AnalyticsData> {
    return this.fetchAPI('/analytics/overview');
  }

  async getDetailedAnalytics(period: string = '30d') {
    return this.fetchAPI(`/analytics/detailed?period=${period}`);
  }

  // RAG System
  async uploadPDF(file: File, description?: string): Promise<{ message: string; file_id: string }> {
    const formData = new FormData();
    formData.append('file', file);
    if (description) {
      formData.append('description', description);
    }

    return fetch(`${API_BASE}/rag/upload`, {
      method: 'POST',
      body: formData,
    }).then(response => {
      if (!response.ok) {
        throw new Error(`Upload failed: ${response.status}`);
      }
      return response.json();
    });
  }

  async searchRAG(query: string, limit: number = 5) {
    return this.fetchAPI('/rag/search', {
      method: 'POST',
      body: JSON.stringify({ query, limit }),
    });
  }

  // Generate study content with AI
  async generateStudyContent(planId: string, topic: string) {
    return this.fetchAPI('/study/generate-content', {
      method: 'POST',
      body: JSON.stringify({ plan_id: planId, topic }),
    });
  }

  // Active Recall questions
  async generateActiveRecallQuestions(topic: string, difficulty: string) {
    return this.fetchAPI('/study/active-recall', {
      method: 'POST',
      body: JSON.stringify({ topic, difficulty }),
    });
  }
}

// Export singleton instance
export const apiService = new APIService();
export default apiService;