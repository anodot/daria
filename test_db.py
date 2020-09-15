from agent import pipeline, source

s = source.repository.get_by_name('monitoring')
s.config['anton'] = 1
source.repository.save(s)
t = 1
