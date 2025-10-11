/**
 * Cycle Phase Service
 * Handles cycle phase detection and change notifications
 */

export interface CyclePhaseInfo {
  phase: 'follicular' | 'ovulatory' | 'luteal' | 'menstrual';
  daysSincePeriod: number;
  phaseDescription: string;
  energyLevel: string;
  hormonalFocus: string;
}

export class CyclePhaseService {
  private static instance: CyclePhaseService;
  private currentPhase: CyclePhaseInfo | null = null;
  private lastCheckDate: string | null = null;

  static getInstance(): CyclePhaseService {
    if (!CyclePhaseService.instance) {
      CyclePhaseService.instance = new CyclePhaseService();
    }
    return CyclePhaseService.instance;
  }

  /**
   * Calculate cycle phase based on last period date and cycle length
   */
  calculateCyclePhase(lastPeriodDate: string, cycleLength: number): CyclePhaseInfo {
    const lastPeriod = new Date(lastPeriodDate);
    const today = new Date();
    const daysSincePeriod = Math.floor((today.getTime() - lastPeriod.getTime()) / (1000 * 60 * 60 * 24));
    
    let phase: 'follicular' | 'ovulatory' | 'luteal' | 'menstrual';
    let phaseDescription: string;
    let energyLevel: string;
    let hormonalFocus: string;

    if (daysSincePeriod <= 5) {
      phase = 'menstrual';
      phaseDescription = 'Your period is active. Focus on rest, iron-rich foods, and gentle movement.';
      energyLevel = 'lowest';
      hormonalFocus = 'iron replenishment, kidney support';
    } else if (daysSincePeriod <= 13) {
      phase = 'follicular';
      phaseDescription = 'Your body is preparing for ovulation. Energy levels are rising - great time for new habits!';
      energyLevel = 'rising';
      hormonalFocus = 'estrogen rising, liver detoxification';
    } else if (daysSincePeriod <= 16) {
      phase = 'ovulatory';
      phaseDescription = 'Peak fertility and energy. Perfect time for challenging activities and social engagement.';
      energyLevel = 'peak';
      hormonalFocus = 'estrogen surge, heart support';
    } else if (daysSincePeriod <= cycleLength - 5) {
      phase = 'luteal';
      phaseDescription = 'Progesterone is rising. Focus on stress management and comfort foods.';
      energyLevel = 'moderate to declining';
      hormonalFocus = 'progesterone support, elimination';
    } else {
      phase = 'menstrual';
      phaseDescription = 'Your period is active. Focus on rest, iron-rich foods, and gentle movement.';
      energyLevel = 'lowest';
      hormonalFocus = 'iron replenishment, kidney support';
    }

    return {
      phase,
      daysSincePeriod,
      phaseDescription,
      energyLevel,
      hormonalFocus
    };
  }

  /**
   * Check if cycle phase has changed since last check
   */
  async checkPhaseChange(lastPeriodDate: string, cycleLength: number): Promise<{
    hasChanged: boolean;
    newPhase: CyclePhaseInfo | null;
    previousPhase: CyclePhaseInfo | null;
  }> {
    const today = new Date().toISOString().split('T')[0];
    
    // Only check once per day
    if (this.lastCheckDate === today) {
      return { hasChanged: false, newPhase: this.currentPhase, previousPhase: null };
    }

    const previousPhase = this.currentPhase;
    const newPhase = this.calculateCyclePhase(lastPeriodDate, cycleLength);
    
    const hasChanged = !this.currentPhase || this.currentPhase.phase !== newPhase.phase;
    
    if (hasChanged) {
      this.currentPhase = newPhase;
      this.lastCheckDate = today;
    }

    return { hasChanged, newPhase, previousPhase };
  }

  /**
   * Get current phase information
   */
  getCurrentPhase(): CyclePhaseInfo | null {
    return this.currentPhase;
  }

  /**
   * Reset phase tracking (useful for testing or user logout)
   */
  reset(): void {
    this.currentPhase = null;
    this.lastCheckDate = null;
  }
}
