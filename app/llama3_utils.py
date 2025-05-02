import json
import random
import torch
import re
from transformers import AutoTokenizer, AutoModelForCausalLM

def build_prompt(fewshot_examples, test_transcription):
    prompt = ""
    for ex in fewshot_examples:
        prompt += f"Transcrição: {ex['transcript']}\nRelatório JSON: {ex['report']}\n\n"
    prompt += f"Transcrição: {test_transcription}\nRelatório JSON:"
    return prompt.strip()

def load_fewshot_examples(jsonl_path, num_shots=3):
    with open(jsonl_path, "r", encoding="utf-8") as f:
        lines = [json.loads(line) for line in f]
    sampled = random.sample(lines, num_shots)
    return [
        {
            "transcript": ex["prompt"].replace("Transcrição: ", "").split("\nGere o relatório")[0].strip(),
            "report": ex["completion"]
        }
        for ex in sampled
    ]



def extract_json(text):
    """
    Extracts the first complete JSON object from the text by tracking braces.
    """
    start = text.find('{')
    if start == -1:
        return None

    open_braces = 0
    for i in range(start, len(text)):
        if text[i] == '{':
            open_braces += 1
        elif text[i] == '}':
            open_braces -= 1
            if open_braces == 0:
                try:
                    candidate = text[start:i+1]
                    json.loads(candidate)  # Try parsing to confirm it's valid
                    return candidate
                except json.JSONDecodeError:
                    break
    return None



def generate_report(transcription, jsonl_path, model_name="meta-llama/Meta-Llama-3-8B-Instruct", num_shots=3, max_new_tokens=1024):
    print("🔍 Generating report for input transcription...")
    fewshots = load_fewshot_examples(jsonl_path, num_shots)
    prompt = build_prompt(fewshots, transcription)

    tokenizer = AutoTokenizer.from_pretrained(model_name, use_auth_token=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="auto",
        use_auth_token=True
    )
    model.eval()

    input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(model.device)

    with torch.no_grad():
        output = model.generate(
            input_ids,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            top_p=0.95,
            temperature=0.7,
            pad_token_id=tokenizer.eos_token_id,
        )

    decoded = tokenizer.decode(output[0], skip_special_tokens=True)
    json_report = extract_json(decoded)

    if json_report:
        print("\n✅ Generated JSON Report:\n")
        print(json_report)
        with open("generated_report.json", "w", encoding="utf-8") as f:
            f.write(json_report)
    else:
        print("⚠️ Could not extract valid JSON from the model output.")
        with open("generated_report.json", "w", encoding="utf-8") as f:
            f.write("")

    return json_report

if __name__ == "__main__":
    transcription_text = (
        "Transcrição: O cavalo foi encaminhado para avaliação devido a rigidez persistente dos membros posteriores e histórico de episódios "
        "intermitentes de desconforto lombar após sessões de treino intensivo. O tutor relatou uma diminuição gradual do rendimento nas últimas "
        "três semanas, associada a episódios de claudicação leve, especialmente após obstáculos. No exame físico estático, observou-se assimetria "
        "da musculatura glútea e sensibilidade à palpação na região lombossacra. A flexão do quadril direito desencadeou resistência, enquanto a "
        "palpação da origem do ligamento suspensor revelou dor bilateral, com maior intensidade no membro posterior esquerdo. No exame dinâmico, "
        "o cavalo apresentou claudicação moderada do MPE na reta, agravada em círculo para a esquerda, com desunião frequente no galope. Foram realizados "
        "bloqueios diagnósticos escalonados, começando pelos nervos digitais plantares e evoluindo até à articulação intertársica distal, com melhoria "
        "progressiva da marcha após o bloqueio da articulação tarsometatársica. As radiografias do tarso mostraram alterações degenerativas ligeiras nas "
        "articulações intertársica distal e tarsometatársica, com presença de osteófitos marginais e estreitamento irregular do espaço articular. "
        "A ultrassonografia revelou alterações fibrilares e perda de definição na origem do ligamento suspensor do boleto, bilateralmente. O tratamento "
        "incluiu infiltração intra-articular com 10mg de triamcinolona no tarso esquerdo e direito, suplementação oral com condroprotetores e início de "
        "fisioterapia com foco em mobilização passiva da região lombossacra. Foi recomendado repouso relativo com trote controlado durante duas semanas, "
        "seguido de trabalho em linha reta em piso macio por quatro semanas. Foi ainda indicada modificação da ferragem com ferraduras de apoio lateral nos "
        "posteriores, reavaliação clínica em 30 dias e nova ecografia antes do regresso ao trabalho completo."
    )

    fewshot_jsonl_path = "/cfs/home/u021554/clinical_report_generation/Clinical_Reports_Dataset/few_shot_learning_data.jsonl"

    generate_report(transcription_text, fewshot_jsonl_path)
