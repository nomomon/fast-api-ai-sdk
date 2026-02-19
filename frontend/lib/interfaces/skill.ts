export interface Skill {
  id: string;
  name: string;
  description: string;
  content: string;
  created_at: string;
  updated_at: string;
}

export interface SkillCreateBody {
  name: string;
  description?: string;
  content?: string;
}

export interface SkillUpdateBody {
  name?: string;
  description?: string;
  content?: string;
}
