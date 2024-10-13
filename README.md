# RZDru_Case

Преобразование каталога товаров ОАО «РЖД».

## Описание

Наше решение поможет компании с легкостью анализировать каталог товаров ОАО «РЖД» благодаря использованию больших языковых моделей и тщательно сформулированных запросов. Благодаря few-shot промтингу и современным LLM, наш алгоритм с высокой точностью извлекает характеристики товаров и формирует детализированный каталог, охватывающий всё разнообразие представленных продуктов.

## Структура репозитория
```
|
├── .gitignore
|
├── README.md                         <- The top-level README for developers using this project
|
├── llm_parser_params.py              <- Итоговая функция извлечения параметров
|
├── parquet_file_researching.ipynb    <- Первичная предобработка датасета
|
├── requirements.txt                  <- Используемые библиотеки
|
├── rzd_case_catalog.ipynb            <- Аналитика и пример пайплайна
```

## Технологический стек

- Language: Python
- Frameworks: Git, HuggingFace
- Libraries: Pandas, Langchain, Llama_index, Transformers
- LLM models: Claude-instant, GigaChat Pro, GPT-4o, GPT-4o mini

## Члены команды

[Смирнов Илья](https://t.me/wsdonbtw)

[Кудряшов Никита](https://t.me/meoskis)

[Заболотная Татьяна](https://t.me/tanushaaz)
