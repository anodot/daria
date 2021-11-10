import os

from agent import pipeline, source, di

di.init()


def clean():
    for pipeline_ in pipeline.repository.get_all():
        pipeline.manager.delete(pipeline_)
    for source_ in source.repository.get_all():
        source.manager.delete(source_)
    folder = '../../../output/'
    if not os.path.isdir(folder):
        print(f'No such directory `{folder}`')
        return
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            os.unlink(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
    print('Cleaned output directory')


if __name__ == '__main__':
    clean()
