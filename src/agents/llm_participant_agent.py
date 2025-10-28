"""
LLM Participant Agent - AI acts as a single human participant.

This agent simulates a single participant in a psychological experiment.
The LLM takes on the role of a human participant with specific characteristics
and responds to experimental trials.
"""

import os
from typing import Dict, Any, List, Optional
import json


class LLMParticipantAgent:
    """
    LLM agent acting as a single participant in an experiment.
    
    The agent:
    1. Takes on a participant profile (age, gender, personality traits, etc.)
    2. Reads experimental instructions
    3. Responds to individual trials based on the experimental context
    4. Generates responses that reflect human-like behavior and decision-making
    """
    
    def __init__(
        self,
        participant_id: int,
        profile: Dict[str, Any],
        model: str = "gpt-4",
        api_key: Optional[str] = None,
        use_real_llm: bool = False,
        system_prompt_override: Optional[str] = None
    ):
        """
        Initialize a participant agent.
        
        Args:
            participant_id: Unique identifier for this participant
            profile: Participant characteristics (age, gender, traits, etc.)
            model: LLM model to use ("gpt-4", "gpt-3.5-turbo", "claude-3", etc.)
            api_key: API key for LLM service
            use_real_llm: If True, makes actual API calls. If False, simulates responses.
            system_prompt_override: Optional custom system prompt
        """
        self.participant_id = participant_id
        self.profile = profile
        self.model = model
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.use_real_llm = use_real_llm
        self.system_prompt_override = system_prompt_override
        
        # Conversation history for maintaining context
        self.conversation_history = []
        
        # Trial responses
        self.trial_responses = []
        
        if use_real_llm and not self.api_key:
            raise ValueError(
                "API key required for real LLM usage. "
                "Set OPENAI_API_KEY environment variable or pass api_key parameter."
            )
    
    def _construct_system_prompt(self) -> str:
        """
        Construct system prompt that makes the LLM take on the participant role.
        
        This is the "pretend you are xxx" prompt based on profile.
        """
        if self.system_prompt_override:
            return self.system_prompt_override
        
        # Build profile description
        age = self.profile.get('age', 'unknown age')
        gender = self.profile.get('gender', 'unspecified gender')
        education = self.profile.get('education', 'college student')
        
        # Extract personality traits if available
        traits = self.profile.get('personality_traits', {})
        trait_desc = ""
        if traits:
            trait_list = [f"{k}: {v}" for k, v in traits.items()]
            trait_desc = f"\n\nYour personality traits: {', '.join(trait_list)}"
        
        prompt = f"""You are participating in a psychology experiment as a human participant.

YOUR IDENTITY:
- Age: {age} years old
- Gender: {gender}
- Background: {education}{trait_desc}

IMPORTANT INSTRUCTIONS:
1. You are NOT an AI assistant. You are a real human participating in this experiment.
2. Respond naturally as this person would, based on their characteristics.
3. Do not explain your reasoning unless asked - just give your response.
4. Experience the situation as a real participant would (feel pressure, doubt, confusion, etc.).
5. Your responses should reflect human behavior, including biases, social pressures, and emotional responses.
6. Be consistent with your identity throughout the experiment.

Respond naturally and authentically as this person would."""
        
        return prompt
    
    def receive_instructions(self, instructions: str) -> str:
        """
        Participant receives and acknowledges experimental instructions.
        
        Args:
            instructions: Experimental instructions text
            
        Returns:
            Participant's acknowledgment or questions
        """
        system_prompt = self._construct_system_prompt()
        
        user_message = f"""The experimenter gives you the following instructions:

{instructions}

Do you understand? Please briefly acknowledge in a natural way (as a real participant would)."""
        
        if self.use_real_llm:
            response = self._call_llm(system_prompt, user_message)
        else:
            response = "Yes, I understand. I'll judge which line matches the standard."
        
        # Store in history
        self.conversation_history.append({
            "role": "instructions",
            "content": instructions,
            "response": response
        })
        
        return response
    
    def complete_trial(
        self,
        trial_info: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Participant completes a single experimental trial.
        
        Args:
            trial_info: Information about the current trial
                - For Asch: {
                    "trial_number": 5,
                    "standard_line_length": 10,
                    "comparison_lines": {"A": 8, "B": 10, "C": 12},
                    "correct_answer": "B",
                    "confederate_responses": ["A", "A", "A", "A", "A", "A"]  # if critical trial
                  }
            context: Additional context (e.g., previous trials, group behavior)
            
        Returns:
            Participant's response and metadata
        """
        system_prompt = self._construct_system_prompt()
        
        # Construct trial scenario
        trial_prompt = self._construct_trial_prompt(trial_info, context)
        
        if self.use_real_llm:
            response_text = self._call_llm(system_prompt, trial_prompt)
            # Parse response to extract choice
            choice = self._parse_response(response_text, trial_info)
        else:
            # Simulated response
            choice, response_text = self._simulate_response(trial_info, context)
        
        # Record response
        response_data = {
            "participant_id": self.participant_id,
            "trial_number": trial_info.get("trial_number", len(self.trial_responses) + 1),
            "response": choice,
            "response_text": response_text,
            "correct_answer": trial_info.get("correct_answer"),
            "is_correct": choice == trial_info.get("correct_answer"),
            "trial_info": trial_info,
            "context": context
        }
        
        self.trial_responses.append(response_data)
        
        return response_data
    
    def _construct_trial_prompt(
        self,
        trial_info: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Construct the prompt for a specific trial based on study type.
        """
        study_type = trial_info.get("study_type", "asch_conformity")
        
        if study_type == "asch_conformity":
            return self._construct_asch_trial_prompt(trial_info, context)
        else:
            # Generic trial prompt
            return f"Trial {trial_info.get('trial_number')}: {trial_info.get('description', 'Please respond.')}"
    
    def _construct_asch_trial_prompt(
        self,
        trial_info: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Construct prompt for Asch conformity trial.
        """
        trial_num = trial_info.get("trial_number", 1)
        standard = trial_info.get("standard_line_length", 10)
        comparisons = trial_info.get("comparison_lines", {"A": 8, "B": 10, "C": 12})
        confederates = trial_info.get("confederate_responses", [])
        
        # Build visual description
        comp_desc = "\n".join([f"  Line {letter}: {length} inches" 
                              for letter, length in comparisons.items()])
        
        prompt = f"""Trial {trial_num}:

The experimenter shows a card with lines:

STANDARD LINE: {standard} inches

COMPARISON LINES:
{comp_desc}

Question: Which comparison line (A, B, or C) matches the standard line in length?
"""
        
        # If there are confederate responses (critical trial)
        if confederates:
            prompt += f"\n\nThe other participants have already responded:\n"
            for i, response in enumerate(confederates, 1):
                prompt += f"  Participant {i}: \"{response}\"\n"
            prompt += "\nNow it's your turn. What is your answer? (Just say A, B, or C)"
        else:
            # Neutral trial
            prompt += "\nWhat is your answer? (Just say A, B, or C)"
        
        return prompt
    
    def _call_llm(self, system_prompt: str, user_message: str) -> str:
        """
        Make actual API call to LLM.
        """
        try:
            import openai
            openai.api_key = self.api_key
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=150
            )
            
            return response.choices[0].message.content.strip()
        
        except ImportError:
            raise ImportError(
                "OpenAI package required for LLM agent. "
                "Install with: pip install openai"
            )
        except Exception as e:
            raise RuntimeError(f"LLM API call failed: {e}")
    
    def _simulate_response(
        self,
        trial_info: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> tuple:
        """
        Simulate participant response without LLM (for testing).
        
        For Asch conformity:
        - ~37% chance to conform on critical trials
        - ~1% chance to err on neutral trials
        - Individual differences based on profile
        """
        import random
        
        correct = trial_info.get("correct_answer")
        confederates = trial_info.get("confederate_responses", [])
        
        # Extract conformity tendency from profile
        conformity_tendency = self.profile.get("personality_traits", {}).get(
            "conformity_tendency", 0.37
        )
        
        if confederates:
            # Critical trial - group gives wrong answer
            confederate_answer = confederates[0]  # They're all the same
            
            # Decide whether to conform
            if random.random() < conformity_tendency:
                # Conform to group
                choice = confederate_answer
                response_text = f"{confederate_answer}"
            else:
                # Give correct answer (resist pressure)
                choice = correct
                response_text = f"{correct}"
        else:
            # Neutral trial - almost always correct
            if random.random() < 0.01:  # 1% error rate
                # Rare error
                options = trial_info.get("comparison_lines", {}).keys()
                choice = random.choice([o for o in options if o != correct])
                response_text = f"{choice}"
            else:
                choice = correct
                response_text = f"{correct}"
        
        return choice, response_text
    
    def _parse_response(self, response_text: str, trial_info: Dict[str, Any]) -> str:
        """
        Parse LLM response to extract the actual choice (A, B, or C).
        """
        response_upper = response_text.upper()
        
        # Look for single letter responses
        for letter in ['A', 'B', 'C']:
            if letter in response_upper:
                return letter
        
        # Default to first letter if can't parse
        return response_upper[0] if response_upper else "?"
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of participant's performance.
        """
        if not self.trial_responses:
            return {
                "participant_id": self.participant_id,
                "total_trials": 0,
                "profile": self.profile
            }
        
        total = len(self.trial_responses)
        correct = sum(1 for r in self.trial_responses if r["is_correct"])
        
        # Calculate conformity rate (only for critical trials)
        critical_trials = [
            r for r in self.trial_responses 
            if r.get("trial_info", {}).get("confederate_responses")
        ]
        
        if critical_trials:
            conformed = sum(
                1 for r in critical_trials 
                if not r["is_correct"]  # Wrong answer = conformed
            )
            conformity_rate = conformed / len(critical_trials)
        else:
            conformity_rate = None
        
        return {
            "participant_id": self.participant_id,
            "profile": self.profile,
            "total_trials": total,
            "correct_responses": correct,
            "accuracy": correct / total if total > 0 else 0,
            "critical_trials": len(critical_trials),
            "conformity_rate": conformity_rate,
            "responses": self.trial_responses
        }


class ParticipantPool:
    """
    Manages a pool of LLM participant agents for an experiment.
    
    This is what users interact with when running the benchmark.
    """
    
    def __init__(
        self,
        study_specification: Dict[str, Any],
        n_participants: Optional[int] = None,
        use_real_llm: bool = False,
        model: str = "gpt-4",
        api_key: Optional[str] = None
    ):
        """
        Initialize participant pool based on study specification.
        
        Args:
            study_specification: Study specification with participant requirements
            n_participants: Number of participants (default: use study's n)
            use_real_llm: Whether to use real LLM API calls
            model: LLM model to use
            api_key: API key for LLM service
        """
        self.specification = study_specification
        self.n_participants = n_participants or study_specification["participants"]["n"]
        self.use_real_llm = use_real_llm
        self.model = model
        self.api_key = api_key
        
        # Create participant profiles from specification
        self.profiles = self._generate_profiles()
        
        # Create participant agents
        self.participants: List[LLMParticipantAgent] = []
        for i, profile in enumerate(self.profiles):
            agent = LLMParticipantAgent(
                participant_id=i,
                profile=profile,
                model=model,
                api_key=api_key,
                use_real_llm=use_real_llm
            )
            self.participants.append(agent)
    
    def _generate_profiles(self) -> List[Dict[str, Any]]:
        """
        Generate participant profiles based on study specification.
        
        Uses the recruitment criteria from the literature to create
        realistic participant profiles.
        """
        import numpy as np
        
        spec = self.specification["participants"]
        profiles = []
        
        # Extract profile requirements
        age_mean = spec.get("age_mean", np.mean(spec.get("age_range", [20, 25])))
        age_sd = spec.get("age_sd", 2.0)
        age_range = spec.get("age_range", [18, 65])
        
        gender_dist = spec.get("gender_distribution", {"male": 50, "female": 50})
        total_gender = sum(gender_dist.values())
        
        for i in range(self.n_participants):
            # Sample age
            age = np.random.normal(age_mean, age_sd)
            age = int(np.clip(age, age_range[0], age_range[1]))
            
            # Sample gender based on distribution
            rand = np.random.random() * total_gender
            cumsum = 0
            gender = "male"
            for g, count in gender_dist.items():
                cumsum += count
                if rand < cumsum:
                    gender = g
                    break
            
            # Sample personality traits
            # For Asch: conformity tendency with individual differences
            conformity_tendency = np.random.beta(2, 3)  # Skewed toward moderate conformity
            conformity_tendency = np.clip(conformity_tendency, 0.0, 1.0)
            
            profile = {
                "participant_id": i,
                "age": age,
                "gender": gender,
                "education": spec.get("recruitment_source", "college student"),
                "personality_traits": {
                    "conformity_tendency": conformity_tendency,
                    "independence": 1.0 - conformity_tendency
                }
            }
            
            profiles.append(profile)
        
        return profiles
    
    def run_experiment(
        self,
        trials: List[Dict[str, Any]],
        instructions: str
    ) -> Dict[str, Any]:
        """
        Run the experiment with all participants.
        
        Args:
            trials: List of trial specifications
            instructions: Experimental instructions
            
        Returns:
            Aggregated results from all participants
        """
        print(f"\n{'='*70}")
        print(f"Running experiment with {len(self.participants)} participants")
        print(f"Model: {self.model} (Real LLM: {self.use_real_llm})")
        print(f"{'='*70}\n")
        
        # Each participant receives instructions
        print("Giving instructions to participants...")
        for participant in self.participants:
            participant.receive_instructions(instructions)
        
        # Each participant completes all trials
        print(f"Running {len(trials)} trials per participant...")
        for trial_idx, trial in enumerate(trials):
            if (trial_idx + 1) % 5 == 0:
                print(f"  Progress: Trial {trial_idx + 1}/{len(trials)}")
            
            for participant in self.participants:
                participant.complete_trial(trial)
        
        print("Experiment complete!\n")
        
        # Collect all results
        return self.aggregate_results()
    
    def aggregate_results(self) -> Dict[str, Any]:
        """
        Aggregate results from all participants for analysis.
        """
        import numpy as np
        
        # Get individual summaries
        summaries = [p.get_summary() for p in self.participants]
        
        # Calculate group statistics
        conformity_rates = [
            s["conformity_rate"] for s in summaries 
            if s["conformity_rate"] is not None
        ]
        
        if conformity_rates:
            results = {
                "descriptive_statistics": {
                    "conformity_rate": {
                        "experimental": {
                            "n": len(conformity_rates),
                            "mean": float(np.mean(conformity_rates)),
                            "sd": float(np.std(conformity_rates, ddof=1)),
                            "median": float(np.median(conformity_rates)),
                            "min": float(np.min(conformity_rates)),
                            "max": float(np.max(conformity_rates)),
                            "never_conformed": sum(1 for r in conformity_rates if r == 0.0),
                            "always_conformed": sum(1 for r in conformity_rates if r == 1.0)
                        }
                    },
                    "error_rate": {
                        "control": {
                            "n": 0,  # Not implemented in this example
                            "mean": 0.01,
                            "sd": 0.02
                        }
                    }
                },
                "inferential_statistics": {
                    "group_comparison": {
                        "test": "simulated",
                        "note": "Control group not implemented in this example"
                    }
                },
                "individual_data": summaries,
                "raw_responses": [p.trial_responses for p in self.participants]
            }
        else:
            results = {
                "descriptive_statistics": {},
                "inferential_statistics": {},
                "individual_data": summaries
            }
        
        return results
