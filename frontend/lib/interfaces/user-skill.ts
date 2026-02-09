export interface UserSkill {
  id: string;
  name: string;
  description: string;
  content: string;
  created_at: string;
  updated_at: string;
}

export interface UserSkillUpdateRequest {
  description?: string;
  content?: string;
}
