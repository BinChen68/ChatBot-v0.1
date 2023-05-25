import openai
import requests


# set Bing Web Search API key
subscription_key = "fe65971cbb184f32a5b4834ad5fa4150"
assert subscription_key
search_url = "https://api.bing.microsoft.com/v7.0/search"


# set OpenAI API key
openai.api_key = "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"
MODEL = "gpt-3.5-turbo"

# set the number of resources returned by Bing Web Search API
resources_num = 3

# prompt need to be carefully designed
template = (
    "You are an intelligent assistant helping Contoso Inc employees with their healthcare plan questions and employee handbook questions. "
    + "Use 'you' to refer to the individual asking the questions even if they ask with 'I'. "
    + "Answer the following question using only the data provided in the sources below. "
    + "For tabular information return it as an html table. Do not return markdown format. "
    + "Each source has a name followed by colon and the actual information, always include the source name for each fact you use in the response. "
    + "If you cannot answer using the sources below, say you don't know. "
    + """

###
Question: 'What is the deductible for the employee plan for a visit to Overlake in Bellevue?'

Sources:
info1.txt: deductibles depend on whether you are in-network or out-of-network. In-network deductibles are $500 for employee and $1000 for family. Out-of-network deductibles are $1000 for employee and $2000 for family.
info2.pdf: Overlake is in-network for the employee plan.
info3.pdf: Overlake is the name of the area that includes a park and ride near Bellevue.
info4.pdf: In-network institutions include Overlake, Swedish and others in the region

Answer:
In-network deductibles are $500 for employee and $1000 for family [info1.txt] and Overlake is in-network for the employee plan [info2.pdf][info4.pdf].

###
Question: 

Sources:

Answer:
"""
)


# initialize the messages with the template
messages = [{"role": "system", "content": template}]


def askChatGPT(messages):
    print('ChatGPT: Ask me something or enter "QUIT" for ending the conversation.\n')
    while True:
        query = input("User: ")
        if query == "QUIT":
            break
        else:
            # ask Bing Web Search API for resources
            resources = askBing(query, resources_num)
            # prepare the prompt
            content = "Question: " + query + "\n" + "Sources:\n"
            for resource_index in range(len(resources)):
                content = content + resources[resource_index]
            content = content + "Answer:\n"
        # give GPT the prepared prompt
        messages.append({"role": "user", "content": content})
        # ask GPT for response
        response = openai.ChatCompletion.create(
            model=MODEL, messages=messages, temperature=1
        )
        chat_response = response.choices[0].message.content

        print(f"ChatGPT: {chat_response}")
        # give GPT the generated response to update history
        messages.append({"role": "assistant", "content": chat_response})


def askBing(query, resources_num):
    # restrict search domain
    search_term = "site:https://open-academy.github.io/machine-learning/ " + query
    headers = {"Ocp-Apim-Subscription-Key": subscription_key}
    params = {"q": search_term, "textDecorations": True, "textFormat": "HTML"}
    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()
    search_results = response.json()
    # select top-n resources and return
    resources = []
    for resource_index in range(resources_num):
        resources.append(
            search_results["webPages"]["value"][resource_index]["url"]
            + ": "
            + search_results["webPages"]["value"][resource_index]["snippet"]
            + "\n"
        )
    return resources


# run
askChatGPT(messages)


# # another possible template
# template = (
#     "Answer the following question using only the data provided in the sources below. Each source has a name followed by colon and the actual information, always include the source name for each fact you use in the response. If you cannot answer using the sources below, say you don't know. Don't answer the question with irrelevant data.\n"
#     + "Question: 'What is the deductible for the employee plan for a visit to Overlake in Bellevue?'\n"
#     + "Sources:\n"
#     + "url_1: deductibles depend on whether you are in-network or out-of-network. In-network deductibles are $500 for employee and $1000 for family. Out-of-network deductibles are $1000 for employee and $2000 for family.\n"
#     + "url_2: Overlake is in-network for the employee plan.\n"
#     + "url_3: Overlake is the name of the area that includes a park and ride near Bellevue.\n"
#     + "url_4: In-network institutions include Overlake, Swedish and others in the region\n"
#     + "Answer:\n"
#     + "In-network deductibles are $500 for employee and $1000 for family [url_1] and Overlake is in-network for the employee plan [url_2][url_4].",
# )
