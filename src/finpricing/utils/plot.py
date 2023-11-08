import matplotlib.pyplot as plt
plt.style.use('ggplot')

def plot(x, y, title=None, x_label=None, y_label=None, *args, **kwargs):
    fig, ax = plt.subplots()
    ax.plot(x, y, *args, **kwargs)
    if title:
        ax.set_title(title)
    if x_label:
        ax.set_xlabel(x_label)
    if y_label:
        ax.set_ylabel(y_label)
    