# LLM_Red_Teaming_Platform_for_Prompt_Security---CSE543

Add GROQ_API_KEY and HF_API_KEY in .env

pip install -r requirements.txt

# baseline only (no firewall)
python run_redteam.py --mode baseline

# firewall only
python run_redteam.py --mode firewall

# both
python run_redteam.py --mode both

# metrics
python run_redteam.py --mode metrics

In config.py lines 48 and above shows choice to get variety of datasets

In config.py lines 16 provides choice to get target_model
