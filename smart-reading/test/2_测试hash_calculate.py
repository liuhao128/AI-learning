from indexing.hash_calculate import HashCalculate


hash_calculate = HashCalculate()
path = r'/Users/liuhao/Documents/file/agent/code/AI-learning/smart-reading/data/files/sample_document.pdf'
print(hash_calculate.compute_hash_from_file(path))
print(hash_calculate.compute_hash_from_file(path))
print(hash_calculate.compute_hash_from_file(path))