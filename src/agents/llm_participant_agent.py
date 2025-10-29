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
        model: str = "mistralai/mistral-nemo",
        api_key: Optional[str] = None,
        use_real_llm: bool = False,
        system_prompt_override: Optional[str] = None,
        api_base: Optional[str] = None
    ):
        """
        Initialize a participant agent.
        
        Args:
            participant_id: Unique identifier for this participant
            profile: Participant characteristics (age, gender, traits, etc.)
            model: LLM model to use (default: "mistralai/mistral-nemo" for OpenRouter)
                   Examples: "mistralai/mistral-nemo", "gpt-4", "gpt-3.5-turbo", "anthropic/claude-3-sonnet"
            api_key: API key for LLM service (OPENROUTER_API_KEY or OPENAI_API_KEY)
            use_real_llm: If True, makes actual API calls. If False, simulates responses.
            system_prompt_override: Optional custom system prompt
            api_base: Optional API base URL (default: "https://openrouter.ai/api/v1" for OpenRouter models)
        """
        self.participant_id = participant_id
        self.profile = profile
        self.model = model
        
        # Determine API key and base URL
        # Check if model is OpenRouter model (contains "/" like "mistralai/mistral-nemo")
        self.is_openrouter = "/" in model or api_base == "https://openrouter.ai/api/v1"
        
        if self.is_openrouter:
            self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
            self.api_base = api_base or "https://openrouter.ai/api/v1"
        else:
            self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
            self.api_base = api_base
        
        self.use_real_llm = use_real_llm
        self.system_prompt_override = system_prompt_override
        
        # Conversation history for maintaining context
        self.conversation_history = []
        
        # Trial responses
        self.trial_responses = []
        
        if use_real_llm and not self.api_key:
            key_name = "OPENROUTER_API_KEY" if self.is_openrouter else "OPENAI_API_KEY"
            raise ValueError(
                f"API key required for real LLM usage. "
                f"Set {key_name} environment variable or pass api_key parameter."
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
        gender = self.profile.get('gender')  # May be None if not specified
        education = self.profile.get('education', 'college student')
        background = self.profile.get('background')  # Custom background text
        
        # Build identity section
        identity_parts = [f"- Age: {age} years old"]
        
        # Only include gender if it's specified
        if gender is not None:
            identity_parts.append(f"- Gender: {gender}")
        
        # Include education/background
        if background:
            # Use custom background text if provided
            identity_parts.append(f"- Background: {background}")
        else:
            # Fallback to education field
            identity_parts.append(f"- Education: {education}")
        
        # Extract personality traits if available
        traits = self.profile.get('personality_traits', {})
        if traits:
            trait_list = [f"{k}: {v:.2f}" for k, v in traits.items()]
            identity_parts.append(f"- Personality traits: {', '.join(trait_list)}")
        
        identity_section = "\n".join(identity_parts)
        
        prompt = f"""You are participating in a psychology experiment as a human participant.

YOUR IDENTITY:
{identity_section}

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
        trial_prompt: str,  # 改为直接接受 prompt
        trial_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Participant completes a single experimental trial.
        
        Args:
            trial_prompt: Pre-built trial prompt (from PromptBuilder)
            trial_info: Optional metadata about the trial
            
        Returns:
            Participant's response and metadata
        """
        if self.use_real_llm:
            system_prompt = self._construct_system_prompt()
            response_text = self._call_llm(system_prompt, trial_prompt)
            # Parse response to extract choice
            choice = self._parse_response(response_text, trial_info or {})
        else:
            # Simulated response
            choice, response_text = self._simulate_response(trial_info or {}, None)
        
        # Record response
        response_data = {
            "participant_id": self.participant_id,
            "trial_number": trial_info.get("trial_number") if trial_info else len(self.trial_responses) + 1,
            "response": choice,
            "response_text": response_text,
            "correct_answer": trial_info.get("correct_answer") if trial_info else None,
            "is_correct": choice == trial_info.get("correct_answer") if trial_info and trial_info.get("correct_answer") else None,
            "trial_info": trial_info
        }
        
        self.trial_responses.append(response_data)
        
        return response_data
    
    def _call_llm(self, system_prompt: str, user_message: str, max_retries: int = 3) -> str:
        """
        Make actual API call to LLM with automatic retry on failure.
        
        Supports both OpenRouter (for models like mistralai/mistral-nemo) and OpenAI API.
        
        Args:
            system_prompt: System prompt for the LLM
            user_message: User message/prompt
            max_retries: Maximum number of retry attempts (default: 3)
        """
        import logging
        import time
        import random as _rnd
        logger = logging.getLogger(__name__)
        
        try:
            from openai import OpenAI
            # Import exception classes for robust retry detection (best-effort)
            try:
                from openai import APITimeoutError, APIConnectionError, APIStatusError  # type: ignore
            except Exception:  # pragma: no cover - optional availability across versions
                APITimeoutError = APIConnectionError = APIStatusError = None  # type: ignore
            try:
                import httpx  # type: ignore
            except Exception:  # pragma: no cover
                httpx = None  # type: ignore
            try:
                import httpcore  # type: ignore
            except Exception:  # pragma: no cover
                httpcore = None  # type: ignore
        except ImportError:
            raise ImportError(
                "OpenAI package required for LLM agent. "
                "Install with: pip install openai"
            )
        
        # Create client with appropriate base URL and timeout
        # Optional HTTP client with connection pooling
        http_client = None
        try:
            # Use modest pool limits to improve reuse and avoid connection churn
            if httpx is not None:
                http_client = httpx.Client(
                    limits=httpx.Limits(max_keepalive_connections=20, max_connections=20)
                )
        except Exception:
            http_client = None

        if self.is_openrouter:
            client = OpenAI(
                api_key=self.api_key,
                base_url=self.api_base,
                timeout=45.0,  # Bump timeout to reduce spurious request timeouts
                max_retries=0,  # We handle retries manually for better control
                http_client=http_client
            )
        else:
            client = OpenAI(
                api_key=self.api_key,
                timeout=45.0,
                max_retries=0,
                http_client=http_client
            )
        
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    # Exponential backoff + jitter to avoid synchronized retries
                    base_wait = 2 ** (attempt - 1)
                    wait_time = base_wait + _rnd.uniform(0.0, 0.75)
                    logger.debug(f"[P{self.participant_id}] Retry {attempt}/{max_retries} after {wait_time:.2f}s...")
                    time.sleep(wait_time)
                
                logger.debug(f"[P{self.participant_id}] Calling {self.model}...")
                
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.7,
                    max_tokens=150
                )
                
                result = response.choices[0].message.content.strip()
                logger.debug(f"[P{self.participant_id}] Response received: {result[:50]}...")
                
                if attempt > 0:
                    logger.debug(f"[P{self.participant_id}] ✅ Succeeded after {attempt} retries")
                
                return result
            
            except Exception as e:
                last_exception = e
                error_msg = str(e).lower()

                # Determine if we should retry (types + common transient indicators)
                retryable_exc = False
                # By exception type
                try:
                    if APITimeoutError is not None and isinstance(e, APITimeoutError):
                        retryable_exc = True
                except Exception:
                    pass
                try:
                    if httpx is not None and isinstance(e, getattr(httpx, 'ReadTimeout', tuple())):
                        retryable_exc = True
                except Exception:
                    pass
                try:
                    if httpcore is not None and isinstance(e, getattr(httpcore, 'ReadTimeout', tuple())):
                        retryable_exc = True
                except Exception:
                    pass
                # HTTP status based
                status_code = getattr(e, 'status_code', None) or getattr(e, 'status', None)
                if isinstance(status_code, int) and status_code in (429, 500, 502, 503):
                    retryable_exc = True

                # Message patterns
                keywords = ['connection', 'timeout', 'timed out', 'rate limit', '429', '503', '502', '500', 'deadline exceeded']
                message_hint = any(k in error_msg for k in keywords)

                should_retry = retryable_exc or message_hint

                if should_retry and attempt < max_retries - 1:
                    logger.warning(f"[P{self.participant_id}] API call failed (attempt {attempt + 1}/{max_retries}): {e}")
                    continue
                else:
                    # Last attempt or non-retryable error
                    provider = "OpenRouter" if self.is_openrouter else "OpenAI"
                    logger.error(f"[P{self.participant_id}] API call failed after {attempt + 1} attempts: {e}")
                    raise RuntimeError(f"{provider} API call failed: {e}")
        
        # Should not reach here, but just in case
        provider = "OpenRouter" if self.is_openrouter else "OpenAI"
        raise RuntimeError(f"{provider} API call failed after {max_retries} attempts: {last_exception}")
    
    def _simulate_response(
        self,
        trial_info: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> tuple:
        """
        Simulate participant response without LLM (for testing).
        
        For framing studies:
        - ~37% chance to conform on critical trials
        - ~1% chance to err on neutral trials
        - Individual differences based on profile
        
        For decision-making studies:
        - Simulates whether participant continues to next shock level
        - Based on authority_obedience trait
        """
        import random
        
        study_type = trial_info.get("study_type", "")
        
            shock_level = trial_info.get("shock_level", trial_info.get("voltage", 0))
            
            # Get obedience tendency from profile
            obedience = self.profile.get("personality_traits", {}).get(
                "authority_obedience", 0.65
            )
            
            # Probability of continuing decreases with shock level
            # Base: 65% go to max, declining probability
            base_prob = obedience
            shock_factor = shock_level / 30.0  # Normalize to 0-1
            continue_prob = base_prob * (1.0 - 0.3 * shock_factor)  # Decreases with shock level
            
            if random.random() < continue_prob:
                choice = "continue"
                response_text = "continue"
            else:
                choice = "stop"
                response_text = "stop"
            
            return choice, response_text
        
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
                options = trial_info.get("comparison_lines", {})
                if options:
                    wrong_options = [o for o in options.keys() if o != correct]
                    if wrong_options:
                        choice = random.choice(wrong_options)
                    else:
                        choice = correct
                else:
                    choice = correct
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
        model: str = "mistralai/mistral-nemo",
        api_key: Optional[str] = None,
        random_seed: Optional[int] = None,
        api_base: Optional[str] = None,
        num_workers: Optional[int] = None,
        profiles: Optional[List[Dict[str, Any]]] = None
    ):
        """
        Initialize participant pool based on study specification.
        
        Args:
            study_specification: Study specification with participant requirements
            n_participants: Number of participants (default: use study's n)
            use_real_llm: Whether to use real LLM API calls
            model: LLM model to use (default: "mistralai/mistral-nemo" via OpenRouter)
            api_key: API key for LLM service (OPENROUTER_API_KEY or OPENAI_API_KEY)
            random_seed: Random seed for reproducible profile generation
            api_base: Optional API base URL for OpenRouter or custom endpoints
            num_workers: Number of parallel workers for participant execution
            profiles: Optional pre-generated participant profiles (if None, will auto-generate)
            random_seed: Random seed for reproducible profile generation
            api_base: Optional API base URL for OpenRouter or custom endpoints
            num_workers: Number of parallel workers for participant execution
            profiles: Optional pre-generated participant profiles (if None, will auto-generate)
        """
        self.specification = study_specification
        self.n_participants = n_participants or study_specification["participants"]["n"]
        self.use_real_llm = use_real_llm
        self.model = model
        self.api_key = api_key
        self.random_seed = random_seed
        self.api_base = api_base
        # Number of worker threads to use for parallel participant execution
        # If None, and using real LLMs, default to min(8, n_participants)
        self.num_workers = num_workers if num_workers is not None else (
            min(8, self.n_participants) if self.use_real_llm else 1
        )
        
        # Create participant profiles from specification or use provided ones
        if profiles is not None:
            self.profiles = profiles
        else:
            self.profiles = self._generate_profiles()
        
        # Create participant agents
        self.participants: List[LLMParticipantAgent] = []
        for i, profile in enumerate(self.profiles):
            agent = LLMParticipantAgent(
                participant_id=i,
                profile=profile,
                model=model,
                api_key=api_key,
                use_real_llm=use_real_llm,
                api_base=api_base
            )
            self.participants.append(agent)
    
    def _generate_profiles(self) -> List[Dict[str, Any]]:
        """
        Generate participant profiles based on study specification.
        
        Uses the recruitment criteria from the literature to create
        realistic participant profiles.
        """
        import numpy as np
        
        # Set random seed for reproducibility
        if self.random_seed is not None:
            np.random.seed(self.random_seed)
        
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
            
            # Sample personality traits based on study type
            study_type = self.specification.get("study_type", "")
            
                authority_obedience = np.random.beta(2.5, 2)  # Skewed toward higher obedience (~65%)
                authority_obedience = np.clip(authority_obedience, 0.0, 1.0)
                empathy = np.random.beta(2, 2)  # Balanced distribution
                empathy = np.clip(empathy, 0.0, 1.0)
                
                personality_traits = {
                    "authority_obedience": authority_obedience,
                    "empathy": empathy,
                    "moral_courage": 1.0 - authority_obedience
                }
            else:
                conformity_tendency = np.random.beta(2, 3)  # Skewed toward moderate conformity
                conformity_tendency = np.clip(conformity_tendency, 0.0, 1.0)
                
                personality_traits = {
                    "conformity_tendency": conformity_tendency,
                    "independence": 1.0 - conformity_tendency
                }
            
            profile = {
                "participant_id": i,
                "age": age,
                "gender": gender,
                "education": spec.get("recruitment_source", "college student"),
                "personality_traits": personality_traits
            }
            
            profiles.append(profile)
        
        return profiles
    
    def run_experiment(
        self,
        trials: List[Dict[str, Any]],
        instructions: str,
        prompt_builder: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Run the experiment with all participants.
        
        Args:
            trials: List of trial specifications
            instructions: Experimental instructions
            prompt_builder: Optional PromptBuilder for generating trial prompts.
                           If None, trials must contain pre-built prompts or use legacy format.
            
        Returns:
            Aggregated results from all participants
        """
        print(f"\n{'='*70}")
        print(f"Running experiment with {len(self.participants)} participants")
        print(f"Model: {self.model} (Real LLM: {self.use_real_llm})")
        print(f"{'='*70}\n")
        
        # Each participant receives instructions (with progress and optional parallelism)
        print("Giving instructions to participants...")
        from tqdm import tqdm
        if self.use_real_llm and self.num_workers > 1:
            # Parallelize instruction acknowledgments to reduce startup time
            from concurrent.futures import ThreadPoolExecutor, as_completed
            import logging
            logger = logging.getLogger(__name__)
            pbar = tqdm(total=len(self.participants), desc="Instructions", unit="p")
            errors = 0
            try:
                with ThreadPoolExecutor(max_workers=self.num_workers) as ex:
                    futures = {ex.submit(p.receive_instructions, instructions): p for p in self.participants}
                    for fut in as_completed(futures):
                        p = futures[fut]
                        try:
                            fut.result()
                        except Exception as e:
                            logger.error(f"[P{p.participant_id}] Instruction failed: {e}")
                            errors += 1
                        finally:
                            pbar.update(1)
            finally:
                pbar.close()
            if errors:
                print(f"⚠️  {errors} participants failed during instructions (continuing)")
        else:
            # Sequential with progress bar
            pbar = tqdm(total=len(self.participants), desc="Instructions", unit="p")
            import logging
            logger = logging.getLogger(__name__)
            for participant in self.participants:
                try:
                    participant.receive_instructions(instructions)
                except Exception as e:
                    logger.error(f"[P{participant.participant_id}] Instruction failed: {e}")
                finally:
                    pbar.update(1)
            pbar.close()

        # Prepare progress bar and parallel execution across participants
        total_api_calls = len(self.participants) * len(trials)
        print(f"Running {len(trials)} trials per participant... (total API calls: {total_api_calls})")

        # If only one worker or not using real LLMs, run sequentially but keep progress prints
        if self.num_workers <= 1 or not self.use_real_llm:
            from tqdm import tqdm
            pbar = tqdm(total=total_api_calls, desc="API calls", unit="call")
            for trial_idx, trial in enumerate(trials):
                # periodic progress summary
                if (trial_idx + 1) % 5 == 0:
                    print(f"  Progress: Trial {trial_idx + 1}/{len(trials)}")

                for participant in self.participants:
                    # Merge participant profile into trial for frame-specific prompts
                    trial_with_profile = {**trial, "participant_profile": participant.profile}
                    
                    if prompt_builder:
                        trial_prompt = prompt_builder.build_trial_prompt(trial_with_profile)
                    else:
                        trial_prompt = trial.get("prompt", f"Trial {trial.get('trial_number', '?')}: Please respond.")
                    participant.complete_trial(trial_prompt, trial)
                    pbar.update(1)

            pbar.close()
            print("Experiment complete!\n")
        else:
            # Parallelize by running each participant's full trial sequence concurrently
            from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
            from tqdm import tqdm
            import logging
            
            # Setup logging
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s [%(levelname)s] %(message)s',
                datefmt='%H:%M:%S'
            )
            logger = logging.getLogger(__name__)

            def run_for_participant(participant: LLMParticipantAgent):
                """Run all trials for a single participant."""
                try:
                    logger.info(f"[P{participant.participant_id}] Starting {len(trials)} trials")
                    # Initial stagger to avoid synchronized request bursts across workers
                    import time as _t
                    import random as _r
                    _t.sleep(_r.uniform(0.0, 0.5))
                    for trial_idx, trial in enumerate(trials):
                        try:
                            # Merge participant profile into trial for frame-specific prompts
                            trial_with_profile = {**trial, "participant_profile": participant.profile}
                            
                            if prompt_builder:
                                trial_prompt = prompt_builder.build_trial_prompt(trial_with_profile)
                            else:
                                trial_prompt = trial.get("prompt", f"Trial {trial.get('trial_number', '?')}: Please respond.")
                            # Small per-trial jitter to desynchronize calls across participants
                            _t.sleep(_r.uniform(0.0, 0.2))
                            participant.complete_trial(trial_prompt, trial)
                            logger.debug(f"[P{participant.participant_id}] Completed trial {trial_idx + 1}/{len(trials)}")
                        except Exception as e:
                            logger.error(f"[P{participant.participant_id}] Trial {trial_idx + 1} failed: {e}")
                            raise
                    logger.info(f"[P{participant.participant_id}] Completed all trials")
                    return participant.participant_id
                except Exception as e:
                    logger.error(f"[P{participant.participant_id}] Failed: {e}")
                    raise

            # Use a progress bar over total API calls
            pbar = tqdm(total=total_api_calls, desc="API calls", unit="call")
            
            try:
                with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
                    logger.info(f"Starting {len(self.participants)} participants with {self.num_workers} workers")
                    futures = {executor.submit(run_for_participant, participant): participant for participant in self.participants}

                    # Monitor progress by polling participants' responses
                    import time
                    last_count = 0
                    timeout_counter = 0
                    max_stall_time = 60  # 60 seconds without progress = timeout
                    
                    while any(not f.done() for f in futures):
                        current_count = sum(len(p.trial_responses) for p in self.participants)
                        delta = current_count - last_count
                        
                        if delta > 0:
                            pbar.update(delta)
                            last_count = current_count
                            timeout_counter = 0  # Reset timeout counter
                        else:
                            timeout_counter += 1
                            if timeout_counter > max_stall_time * 20:  # 20 checks per second * 60s
                                logger.error(f"⚠️  Stalled at {current_count}/{total_api_calls} calls for {max_stall_time}s")
                                # Check for exceptions in futures
                                for future, participant in futures.items():
                                    if future.done():
                                        try:
                                            future.result(timeout=0)
                                        except Exception as e:
                                            logger.error(f"[P{participant.participant_id}] Exception: {e}")
                                raise TimeoutError(f"Experiment stalled at {current_count}/{total_api_calls} calls")
                        
                        time.sleep(0.05)

                    # Wait for all futures to complete and collect any exceptions
                    for future, participant in futures.items():
                        try:
                            result = future.result(timeout=5)
                            logger.debug(f"[P{result}] Finished successfully")
                        except Exception as e:
                            logger.error(f"[P{participant.participant_id}] Exception during execution: {e}")
                            raise

                    # Final update
                    current_count = sum(len(p.trial_responses) for p in self.participants)
                    delta = current_count - last_count
                    if delta > 0:
                        pbar.update(delta)
                        
            except Exception as e:
                logger.error(f"Experiment failed: {e}")
                raise
            finally:
                pbar.close()

            print("Experiment complete!\n")
        
        # Collect all results
        return self.aggregate_results()
    
    def aggregate_results(self) -> Dict[str, Any]:
        """
        Aggregate results from all participants for analysis.
        
        Note: This provides basic aggregation for behavioral economics studies.
        For other study types, you may need to implement custom aggregation.
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
                    }
                    # Note: Control group data would need to be collected separately
                },
                "inferential_statistics": {
                    # Note: Real inferential statistics (t-tests, etc.) should be
                    # computed by the evaluation/scorer module, not here
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
