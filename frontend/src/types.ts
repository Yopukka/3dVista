export interface Client {
  id: number;
  name: string;
  company: string;
  logo_url: string;
  primary_color: string;
  tour_url: string;
  created_at: string;
  results_count: number;
}

export interface TourResult {
  id: number;
  client: number;
  employee_name: string;
  score: number;
  total_score: number;
  answered_questions: number;
  total_questions: number;
  items_found: number;
  total_items: number;
  completed_at: string;
}
