import matplotlib.pyplot as plt

labels = ['Can Run', 'Import Error', 'Error in Code', 'Incomplete Response', 'Inheritance Error', 'All Fail']
base =     [10, 29, 0, 0, 0, 1]
finetuned =[22, 10, 1, 4, 3, 0]

x = range(len(labels))
width = 0.35

plt.figure(figsize=(10, 6))
plt.barh(x, base, width, label='Base Model', alpha=0.7)
plt.barh([i + width for i in x], finetuned, width, label='Fine-Tuned Model', alpha=0.7)

plt.yticks([i + width / 2 for i in x], labels)
plt.xlabel('Number of Test Results')
plt.title('Python Unit Test Generation: Base vs Fine-Tuned Model')
plt.legend()
plt.grid(axis='x', linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()