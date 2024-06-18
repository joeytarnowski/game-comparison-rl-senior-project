import pickle

name = ['q_agent.pkl', 'sarsa_agent.pkl', 'mcoff_agent.pkl','mcon_agent.pkl']
for i in name:
    with open(f'Web/{i}', 'rb') as f:
        agent = pickle.load(f)

    with open(f'Dictionaries/{i}', 'wb') as f:
        pickle.dump(agent.Q, f)