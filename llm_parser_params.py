import requests
import json
import time


def get_answer(prompt, system_prompt, ai_key, model="gpt-4o-mini"):
  url = "https://gptunnel.ru/v1/chat/completions"
  headers = {
      "Authorization": f"Bearer {ai_key}",
      "Content-Type": "application/json"
  }
  data = {
      "model": model,
      "messages": [
          {
              "role": "system",
              "content": system_prompt
          },
          {
              "role": "user",
              "content": prompt
          }
      ]
  }
  response = requests.post(url, headers=headers, data=json.dumps(data))
  return response.json()


def get_answer_v2(prompt, client, model='gpt-4o-mini', system_prompt=None):
  if system_prompt:
    completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        max_tokens=20000, 
        model=model 
    )
  else:
    completion = client.chat.completions.create(
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=20000, 
        model=model
    )
  return completion



def get_list_of_dicts_llm(df, ai_key, path_to_save='/content/drive/MyDrive/HACKS/РЖД 12.10.2024/'):

  df_top_okpd = df.okpd.value_counts().to_frame()
  okpd_list = df_top_okpd.index.to_list() # <--------#####---------#####---------#####------ лист с окпд группами
  okpd_names = df[df.okpd.isin(okpd_list)].drop_duplicates(subset='okpd').set_index('okpd').to_dict()['OKPD2_NAME'] 
  print('Первая итерация')

  samples = {name: [] for name in okpd_list}
  samples_id = {name: [] for name in okpd_list}

  for i, items in enumerate(samples.items()):
    key, value = items
    tmp = df[df.okpd == key].sample(4)[['id', 'name', 'params']]
    print(f'Выполнено: {round(i/(len(samples)-1), 3)*100}%')

    for j in range(4):
      product_name = tmp['name'].iloc[j]
      product_params = tmp['params'].iloc[j]

      system_prompt = "Ты должен максимально корректно и локанично находить имена для характеристик, маскимально обобщая их названия"
      prompt = f"""
  Тебе нужно разделить каждую характеристику продукта в формате JSON, ничего лишнего
  Каждый продукт обладает своими характеристиками. Описание продукта не требуется.
  Характеристики могут быть описаны буквально или через "=", например D=42, это обозначение диаметра 42мм

  Пример вывода ответа
  {{
      'Характеристика 1': 'Значение характеристики 1', 
      'Характеристика 2': 'Значение характеристики 2', 
      'Характеристика 3': 'Значение характеристики 3'
  }}

  Определи название характеристик:
  Продукт - {product_name}
  Характеристики: {product_params}
      """
      completion = get_answer(
          prompt=prompt,
          system_prompt=system_prompt,
          ai_key=ai_key,
          model='gpt-4o'
      )

      samples[key].append(completion)
      samples_id[key].append(tmp['id'].iloc[j])



  wanna_cry = {key: [value['choices'][0]['message']['content'] for value in values] for key, values in samples.items()}

  examples = {}
  for key in wanna_cry.keys():
    result_list = []
    for data in wanna_cry[key]:
      jsn = data.replace('json', '').replace('```', '').replace("'", '"').replace('/n', '')
      jsn = json.loads(jsn)
      result_list.append(jsn)
    examples[key] = result_list


  start = time.time()
  total_parsed_params = [] # <--------#####---------#####---------#####------ сюда все сохраняется

  for k in range(df_top_okpd.shape[0]):
    key = df_top_okpd.reset_index()['okpd'].iloc[k]

    # для реализации промпта
    ids = ['1', '30', '59385', '3993']
    for i in range(4):
      examples[key][i] = {'Параметры': examples[key][i]}
      examples[key][i]['id'] = ids[i]

    shape_key = df[df.okpd == key].shape[0]
    for i in range(0, shape_key, 100):
      print('Прошло минут: ', round((time.time() - start)/60, 1))
      # print('Количество распаршеных строк: ', len(total_parsed_params))
      print(f'ОДКП2: {key} ({k}), выполнено ключей: {round(k/(df_top_okpd.shape[0]-1), 3)*100},\n{i}. Процент выполнения в этом ключе: {round(i/(shape_key-1), 3)*100}%\n')
      tmp_ = df[df.okpd == key].iloc[i:i+100][['index', 'params']]
      params_to_llm = ('ID: ' + tmp_['index'].str[:] + '. Параметры:' + tmp_['params'].str[:]).to_list()
      params_to_llm = '\n'.join(params_to_llm)

      okpd_name = okpd_names[key]

      system_prompt = """
Ты должен максимально корректно и локанично находить имена для характеристик, маскимально обобщая их названия
Формат вывода: {{'id': "заданный id", Параметры: ['Характеристика 1': 'Значение 1', 'Характеристика 2': 'Значение 2', ...]}, {...}}
"""
      prompt = f'''
Тебе нужно разделить каждую характеристику продукта в формате JSON (словарь python), ничего лишнего.
Все продукты относятся к классу продуктов "{okpd_name}"
Каждый продукт обладает своими характеристиками. Описание продукта не требуется
Для каждого продукта необходимо занести в параметры его id

Пример 1:
ID: 1. Параметры: {df.loc[df.id == samples_id[key][0], 'params'].iloc[0]}
Ответ:
{examples[key][0]}

Пример 2:
ID: 30. Параметры: {df.loc[df.id == samples_id[key][1], 'params'].iloc[0]}
Ответ:
{examples[key][1]}

Пример 3:
ID: 59385. Параметры: {df.loc[df.id == samples_id[key][2], 'params'].iloc[0]}
Ответ:
{examples[key][2]}

Пример 4:
ID: 3993. Параметры: {df.loc[df.id == samples_id[key][3], 'params'].iloc[0]}
Ответ:
{examples[key][3]}

Параметры:
{params_to_llm}
      '''

      completion = get_answer(
          prompt=prompt,
          system_prompt=system_prompt,
          ai_key=ai_key,
          model='gpt-4o-mini', 
      )

      wanna_cry_pro = completion['choices'][0]['message']['content']
      file_name = f'model_output_iter_{int(i/100)}.json'
      with open(path_to_save+file_name, 'w', encoding='utf-8') as json_file:
        json.dump(wanna_cry_pro, json_file, ensure_ascii=False, indent=4)

  #     wanna_cry_pro = json.loads(wanna_cry_pro.replace('json', '').replace('```', '').replace('\n', '').replace("},", "}").replace("}", "}, ").replace("'", '"'))
  #     for d in wanna_cry_pro:
  #         if "ID" in d:
  #             d["id"] = d.pop("ID")
  #             d["id"] = str(d["id"])
  #     total_parsed_params += wanna_cry_pro

  # return total_parsed_params