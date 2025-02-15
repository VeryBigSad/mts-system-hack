import torch
import yaml
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import get_peft_model, LoraConfig, TaskType
from datasets import Dataset
import json
from typing import Dict, List

def load_dataset(dataset_path: str) -> Dataset:
    """Загрузка готового датасета"""
    with open(dataset_path, 'r', encoding='utf-8') as f:
        examples = json.load(f)
    
    # Преобразуем примеры в формат для обучения
    training_data = []
    for example in examples:
        # Форматируем каждый пример в единый текст
        formatted_text = f"### Задача:\n{example}\n\n"
        training_data.append({"text": formatted_text})
    
    return Dataset.from_list(training_data)

def train_model(config_path: str):
    # Загружаем конфиг
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Загружаем готовый датасет
    dataset = load_dataset(config['data']['dataset_path'])
    
    # Инициализируем токенизатор и модель
    tokenizer = AutoTokenizer.from_pretrained(config['model']['base_model'])
    model = AutoModelForCausalLM.from_pretrained(
        config['model']['base_model'],
        torch_dtype=torch.float16 if config['training']['fp16'] else torch.float32,
        device_map="auto"
    )
    
    # Конфигурация LoRA
    peft_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        inference_mode=False,
        r=config['model']['lora']['r'],
        lora_alpha=config['model']['lora']['alpha'],
        lora_dropout=config['model']['lora']['dropout'],
        target_modules=config['model']['lora']['target_modules']
    )
    
    # Применяем LoRA к модели
    model = get_peft_model(model, peft_config)
    
    # Токенизируем датасет
    def tokenize_function(examples):
        return tokenizer(
            examples["text"],
            padding="max_length",
            truncation=True,
            max_length=config['data']['max_seq_length']
        )
    
    tokenized_dataset = dataset.map(
        tokenize_function,
        batched=True,
        remove_columns=dataset.column_names
    )
    
    # Аргументы для обучения
    training_args = TrainingArguments(
        output_dir=config['output']['dir'],
        num_train_epochs=config['training']['num_epochs'],
        per_device_train_batch_size=config['training']['batch_size'],
        gradient_accumulation_steps=config['training']['gradient_accumulation_steps'],
        learning_rate=config['training']['learning_rate'],
        weight_decay=config['training']['weight_decay'],
        warmup_steps=config['training']['warmup_steps'],
        logging_dir=config['output']['logging_dir'],
        logging_steps=config['validation']['logging_steps'],
        save_steps=config['validation']['save_steps'],
        eval_steps=config['validation']['eval_steps'],
        fp16=config['training']['fp16'],
        seed=config['seed']
    )
    
    # Инициализируем тренер
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False)
    )
    
    # Запускаем обучение
    trainer.train()
    
    # Сохраняем обученную модель
    trainer.save_model()
    
if __name__ == "__main__":
    train_model("config.yaml")
