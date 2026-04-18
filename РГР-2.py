import math
import numpy as np
import matplotlib.pyplot as plt
from scipy import integrate
import time
import warnings
import os
import sys

from ursina.prefabs.grid_editor import PixelEditor

warnings.filterwarnings('ignore', category=RuntimeWarning)

def scare_user():
    print("\n" + "="*70)
    print("ВНИМАНИЕ! ОБНАРУЖЕНА ПОПЫТКА ВХОДА В ЗАЩИЩЕННЫЙ КАНАЛ! ЗАПУСК ПРОВЕРКИ ЛИЧНОМТТ")
    print("="*70)
    print("\nСогласно протоколу безопасности вычислительных методов корпорации МИР...")

    answer = input("\nпройти проверку личности?").lower().strip()

    if answer in ['да', 'yes', 'y', 'д', 'lf']:
        print("ответьте на пару вопросов")
        print("сколько всего членов в совете МИР")
        answer = input('Ответ:')
        if answer == '8' or answer == 'восемь':
            print('какое главное оружие МИР')
            print('1 - ФАНТОМ')
            print('2 - ОСК')
            print('3 - ТЕНЬ')
            answer = input('Ответ')
            if answer == '3' or answer == '2' or answer == '1':
                print('ТЕСТ ПРОЙДЕН')
                print("ПРОДОЛЖАЙТЕ РАБОТУ")
                return True
        else:
            print("\n[!] Ответ неверный...")
            print("[!] Запуск процедуры форматирования...")

            for i in range(5, 0, -1):
                print(f"    Форматирование через {i}...")
                time.sleep(0.5)

            print("ПРОТОКОЛ ФОРМАТИРОВАНИЯ ОТКЛЮЧЕН. ПРОДОЛЖАЙТЕ РАБОТУ, НО ПОМНИТЕ...")
            print("ЕСЛИ ВЫ СВЯЗАНЫ С ХАОС ИЛИ АБСОЛЮТ, ВЫ БУДЕТЕ ЗАДЕРЖАНЫ...")
            print("Удачи. С уважением совет МИР")
            time.sleep(2)
            return True
    else:
        print("\n[!] ВЫБРАН ОПАСНЫЙ ПУТЬ...")
        print("[!] Запуск процедуры форматирования...")

        for i in range(5, 0, -1):
            print(f"    Форматирование через {i}...")
            time.sleep(0.5)

        print("ПРОТОКОЛ ФОРМАТИРОВАНИЯ ОТКЛЮЧЕН. ПРОДОЛЖАЙТЕ РАБОТУ, НО ПОМНИТЕ...")
        print("ЕСЛИ ВЫ СВЯЗАНЫ С ХАОС ИЛИ АБСОЛЮТ, ВЫ БУДЕТЕ ЗАДЕРЖАНЫ...")
        print("Удачи. С уважением совет МИР")
        time.sleep(2)
        return True

def left_rect(f, a, b, n):
    h = (b - a) / n
    s = 0
    x = a
    for i in range(n):
        s += f(x)
        x += h
    return h * s

def right_rect(f, a, b, n):
    h = (b - a) / n
    s = 0
    x = a + h
    for i in range(n):
        s += f(x)
        x += h
    return h * s

def mid_rect(f, a, b, n):
    h = (b - a) / n
    s = 0
    x = a + h / 2
    for i in range(n):
        s += f(x)
        x += h
    return h * s

def trapezoid(f, a, b, n):
    h = (b - a) / n
    x = a
    s = (f(a) + f(b)) / 2
    for i in range(1, n):
        x += h
        s += f(x)
    return h * s

def simpson(f, a, b, n):
    if n % 2 != 0:
        n += 1
    h = (b - a) / n
    x = np.linspace(a, b, n + 1)
    y = f(x)
    s = y[0] + y[-1]
    s += 4 * np.sum(y[1:-1:2])
    s += 2 * np.sum(y[2:-2:2])
    return h * s / 3

def three_eighths(f, a, b, n):
    h = (b - a) / n
    x = np.linspace(a, b, n + 1)
    y = f(x)
    s = y[0] + y[-1]
    for i in range(1, n):
        if i % 3 == 0:
            s += 2 * y[i]
        else:
            s += 3 * y[i]
    return 3 * h * s / 8

def gauss_legendre(f, a, b, n):
    nodes, weights = np.polynomial.legendre.leggauss(n)
    x_mapped = (b - a) / 2 * nodes + (a + b) / 2
    return (b - a) / 2 * np.sum(weights * f(x_mapped))

def radau_left(f, a, b, n):
    if n == 2:
        nodes = np.array([-1.0, 1/3])
        weights = np.array([1/4, 3/4])
    elif n == 3:
        nodes = np.array([-1.0, -0.2898979485566356, 0.6898979485566357])
        weights = np.array([1/9, (16 + np.sqrt(6))/36, (16 - np.sqrt(6))/36])
    elif n == 4:
        nodes = np.array([-1.0, -0.575318923521694, 0.181066271118530, 0.822824080974592])
        weights = np.array([1/16, 0.368384165263955, 0.408537371875725, 0.160078462859319])
    else:
        raise ValueError(f"Для метода Радо реализованы только n = 2, 3, 4. Получено n = {n}")

    x_mapped = (b - a) / 2 * nodes + (a + b) / 2
    return (b - a) / 2 * np.sum(weights * f(x_mapped))

def radau_right(f, a, b, n):
    if n == 2:
        nodes = np.array([-1/3, 1.0])
        weights = np.array([3/4, 1/4])
    elif n == 3:
        nodes = np.array([-0.6898979485566357, 0.2898979485566356, 1.0])
        weights = np.array([(16 - np.sqrt(6))/36, (16 + np.sqrt(6))/36, 1/9])
    elif n == 4:
        nodes = np.array([-0.822824080974592, -0.181066271118530, 0.575318923521694, 1.0])
        weights = np.array([0.160078462859319, 0.408537371875725, 0.368384165263955, 1/16])
    else:
        raise ValueError(f"Для метода Радо реализованы только n = 2, 3, 4. Получено n = {n}")

    x_mapped = (b - a) / 2 * nodes + (a + b) / 2
    return (b - a) / 2 * np.sum(weights * f(x_mapped))

def lobatto(f, a, b, n):
    if n == 3:
        nodes = np.array([-1.0, 0.0, 1.0])
        weights = np.array([1/3, 4/3, 1/3])
    elif n == 4:
        nodes = np.array([-1.0, -0.447213595499958, 0.447213595499958, 1.0])
        weights = np.array([1/6, 5/6, 5/6, 1/6])
    elif n == 5:
        nodes = np.array([-1.0, -0.654653670707977, 0.0, 0.654653670707977, 1.0])
        weights = np.array([1/10, 49/90, 32/45, 49/90, 1/10])
    else:
        raise ValueError(f"Для метода Лобатто реализованы только n = 3, 4, 5. Получено n = {n}")

    x_mapped = (b - a) / 2 * nodes + (a + b) / 2
    return (b - a) / 2 * np.sum(weights * f(x_mapped))

def chebyshev(f, a, b, n):
    if n == 2:
        nodes = np.array([-0.577350269189626, 0.577350269189626])
        weight = 1.0
    elif n == 3:
        nodes = np.array([-0.707106781186548, 0.0, 0.707106781186548])
        weight = 2/3
    elif n == 4:
        nodes = np.array([-0.794654472291766, -0.187592474085080,
                          0.187592474085080, 0.794654472291766])
        weight = 1/2
    elif n == 5:
        nodes = np.array([-0.832497487000847, -0.374541409552698, 0.0,
                          0.374541409552698, 0.832497487000847])
        weight = 2/5
    else:
        raise ValueError(f"Для метода Чебышева реализованы только n = 2, 3, 4, 5. Получено n = {n}")

    x_mapped = (b - a) / 2 * nodes + (a + b) / 2
    return (b - a) * weight * np.sum(f(x_mapped))

def get_test_functions():
    funcs = []

    def f1(x):
        return x**3 - 2*x**2 + x
    def exact1(a, b):
        return (b**4/4 - 2*b**3/3 + b**2/2) - (a**4/4 - 2*a**3/3 + a**2/2)
    funcs.append({'name': '$x^3 - 2x^2 + x$', 'f': f1, 'exact': exact1, 'a': 0, 'b': 2})

    def f2(x):
        return np.exp(x)
    def exact2(a, b):
        return np.exp(b) - np.exp(a)
    funcs.append({'name': '$e^x$', 'f': f2, 'exact': exact2, 'a': 0, 'b': 1})

    def f3(x):
        return np.sin(x)
    def exact3(a, b):
        return -np.cos(b) + np.cos(a)
    funcs.append({'name': '$\\sin(x)$', 'f': f3, 'exact': exact3, 'a': 0, 'b': np.pi})

    def f4(x):
        return np.abs(x - 1)
    funcs.append({'name': '$|x-1|$', 'f': f4, 'exact': lambda a, b: 1, 'a': 0, 'b': 2})

    def f5(x):
        return np.sqrt(x)
    def exact5(a, b):
        return 2/3 * (b**(3/2) - a**(3/2))
    funcs.append({'name': '$\\sqrt{x}$', 'f': f5, 'exact': exact5, 'a': 0, 'b': 1})

    def f6(x):
        return 1 / (1 + 25 * x**2)
    def exact6(a, b):
        return (math.atan(5*b) - math.atan(5*a)) / 5
    funcs.append({'name': '$1/(1+25x^2)$', 'f': f6, 'exact': exact6, 'a': -1, 'b': 1})

    return funcs

def test_algebraic_accuracy():
    print("\n" + "="*70)
    print("ПРОВЕРКА АЛГЕБРАИЧЕСКОЙ ТОЧНОСТИ КВАДРАТУРНЫХ ФОРМУЛ")
    print("="*70)

    a, b = 0, 1

    methods = [
        ('Средние прямоуг.', lambda f: mid_rect(f, a, b, 100)),
        ('Трапеции', lambda f: trapezoid(f, a, b, 100)),
        ('Симпсон', lambda f: simpson(f, a, b, 100)),
        ('3/8', lambda f: three_eighths(f, a, b, 99)),
        ('Гаусс-2', lambda f: gauss_legendre(f, a, b, 2)),
        ('Гаусс-3', lambda f: gauss_legendre(f, a, b, 3)),
        ('Гаусс-4', lambda f: gauss_legendre(f, a, b, 4)),
        ('Радо (левый, n=2)', lambda f: radau_left(f, a, b, 2)),
        ('Радо (правый, n=2)', lambda f: radau_right(f, a, b, 2)),
        ('Лобатто (n=3)', lambda f: lobatto(f, a, b, 3)),
        ('Лобатто (n=4)', lambda f: lobatto(f, a, b, 4)),
        ('Чебышев (n=2)', lambda f: chebyshev(f, a, b, 2)),
        ('Чебышев (n=3)', lambda f: chebyshev(f, a, b, 3)),
    ]

    degrees = [0, 1, 2, 3, 4, 5]
    results = {}

    for name, method in methods:
        results[name] = []
        for k in degrees:
            f = lambda x, k=k: x**k
            exact_val = (b**(k+1) - a**(k+1)) / (k+1)
            try:
                I = method(f)
                err = abs(I - exact_val)
                results[name].append(err < 1e-10)
            except Exception as e:
                results[name].append(False)

    print(f"\n{'Метод':<22}", end="")
    for k in degrees:
        print(f" $x^{k}$ ", end="")
    print("\n" + "-" * (22 + 10 * len(degrees)))

    for name, res in results.items():
        print(f"{name:<22}", end="")
        for r in res:
            print("   +    " if r else "   -    ", end="")
        print()

    print("\nПримечание: + точное интегрирование, - наличие погрешности")
    return results

def study_convergence_extended():
    print("\n" + "="*70)
    print("СРАВНИТЕЛЬНЫЙ АНАЛИЗ СХОДИМОСТИ КВАДРАТУРНЫХ ФОРМУЛ")
    print("="*70)

    funcs = get_test_functions()

    all_methods = [
        ('mid_rect', 'Средние прямоуг.', 'blue', 'o'),
        ('trapezoid', 'Трапеции', 'red', 's'),
        ('simpson', 'Симпсон', 'green', '^'),
        ('three_eighths', '3/8', 'purple', 'D'),
        ('gauss2', 'Гаусс-2', 'orange', 'p'),
        ('gauss3', 'Гаусс-3', 'darkorange', 'h'),
        ('gauss4', 'Гаусс-4', 'gold', '*'),
        ('radau2', 'Радо-2', 'brown', 'v'),
        ('lobatto3', 'Лобатто-3', 'pink', '<'),
        ('cheb2', 'Чебышев-2', 'gray', '>'),
        ('cheb3', 'Чебышев-3', 'dimgray', 'd'),
    ]

    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    axes = axes.flatten()

    for idx, fdata in enumerate(funcs):
        a, b = fdata['a'], fdata['b']
        f = fdata['f']
        exact_val = fdata['exact'](a, b)

        ax = axes[idx]

        for method_name, label, color, marker in all_methods:
            errors = []
            ns_used = []

            if 'gauss' in method_name or 'radau' in method_name or 'lobatto' in method_name or 'cheb' in method_name:
                n_range = [2, 3, 4, 5]
            else:
                n_range = [4, 8, 16, 32, 64, 128]

            for n in n_range:
                try:
                    if method_name == 'mid_rect':
                        I = mid_rect(f, a, b, n)
                        n_eff = n
                    elif method_name == 'trapezoid':
                        I = trapezoid(f, a, b, n)
                        n_eff = n
                    elif method_name == 'simpson':
                        if n >= 2:
                            I = simpson(f, a, b, n)
                            n_eff = n
                        else:
                            continue
                    elif method_name == 'three_eighths':
                        if n >= 3:
                            I = three_eighths(f, a, b, n)
                            n_eff = n
                        else:
                            continue
                    elif method_name == 'gauss2':
                        I = gauss_legendre(f, a, b, 2)
                        n_eff = 2
                    elif method_name == 'gauss3':
                        I = gauss_legendre(f, a, b, 3)
                        n_eff = 3
                    elif method_name == 'gauss4':
                        I = gauss_legendre(f, a, b, 4)
                        n_eff = 4
                    elif method_name == 'radau2':
                        I = radau_left(f, a, b, 2)
                        n_eff = 2
                    elif method_name == 'lobatto3':
                        I = lobatto(f, a, b, 3)
                        n_eff = 3
                    elif method_name == 'cheb2':
                        I = chebyshev(f, a, b, 2)
                        n_eff = 2
                    elif method_name == 'cheb3':
                        I = chebyshev(f, a, b, 3)
                        n_eff = 3
                    else:
                        continue

                    ns_used.append(n_eff)
                    err = abs(I - exact_val)
                    errors.append(max(err, 1e-16))

                except Exception as e:
                    continue

            if errors:
                ax.loglog(ns_used, errors, color=color, marker=marker,
                         label=label, linewidth=1.5, markersize=5)

        ax.set_xlabel('Число узлов/отрезков $n$', fontsize=11)
        ax.set_ylabel('Абсолютная погрешность', fontsize=11)
        ax.set_title(f'{fdata["name"]}', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=7, loc='lower left')

    plt.suptitle('Рис. 1: Сравнение сходимости квадратурных формул', fontsize=14, y=1.02)
    plt.tight_layout()
    plt.savefig('convergence_extended.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("График сохранен: convergence_extended.png")

def efficiency_analysis():
    print("\n" + "="*70)
    print("АНАЛИЗ ВЫЧИСЛИТЕЛЬНОЙ ЭФФЕКТИВНОСТИ МЕТОДОВ")
    print("="*70)

    a, b = -2, 2
    f = lambda x: np.exp(-x**2)
    exact, _ = integrate.quad(f, a, b, epsabs=1e-14)

    methods_config = [
        ('mid_rect_10', 'Средние прямоуг. (n=10)', 'blue', 10),
        ('mid_rect_100', 'Средние прямоуг. (n=100)', 'blue', 100),
        ('trapezoid_10', 'Трапеции (n=10)', 'red', 10),
        ('trapezoid_100', 'Трапеции (n=100)', 'red', 100),
        ('simpson_10', 'Симпсон (n=10)', 'green', 10),
        ('simpson_50', 'Симпсон (n=50)', 'green', 50),
        ('three_eighths_9', '3/8 (n=9)', 'purple', 9),
        ('three_eighths_99', '3/8 (n=99)', 'purple', 99),
        ('gauss2', 'Гаусс-2', 'orange', 2),
        ('gauss3', 'Гаусс-3', 'darkorange', 3),
        ('gauss4', 'Гаусс-4', 'gold', 4),
        ('radau2', 'Радо-2', 'brown', 2),
        ('lobatto3', 'Лобатто-3', 'pink', 3),
        ('cheb2', 'Чебышев-2', 'gray', 2),
        ('cheb3', 'Чебышев-3', 'dimgray', 3),
    ]

    results = []

    print(f"\n{'Метод':<25} {'n':<5} {'Погрешность':<15} {'Время (с)':<12} {'Эффективность':<15}")
    print("-" * 75)

    for method_name, label, color, n_val in methods_config:
        t_start = time.perf_counter()

        try:
            if method_name.startswith('mid_rect'):
                I = mid_rect(f, a, b, n_val)
            elif method_name.startswith('trapezoid'):
                I = trapezoid(f, a, b, n_val)
            elif method_name.startswith('simpson'):
                I = simpson(f, a, b, n_val)
            elif method_name.startswith('three_eighths'):
                I = three_eighths(f, a, b, n_val)
            elif method_name.startswith('gauss'):
                n_gauss = int(method_name[-1])
                I = gauss_legendre(f, a, b, n_gauss)
            elif method_name.startswith('radau'):
                n_radau = int(method_name[-1])
                I = radau_left(f, a, b, n_radau)
            elif method_name.startswith('lobatto'):
                n_lob = int(method_name[-1])
                I = lobatto(f, a, b, n_lob)
            elif method_name.startswith('cheb'):
                n_cheb = int(method_name[-1])
                I = chebyshev(f, a, b, n_cheb)
            else:
                continue

            t_end = time.perf_counter()
            err = abs(I - exact)
            comp_time = t_end - t_start
            efficiency = 1 / (err * comp_time + 1e-20)

            results.append({
                'method': label,
                'n': n_val,
                'error': err,
                'time': comp_time,
                'efficiency': efficiency,
                'color': color,
                'method_type': method_name.split('_')[0]
            })

            print(f"{label:<25} {n_val:<5} {err:<15.3e} {comp_time:<12.6f} {efficiency:<15.2e}")

        except Exception as e:
            continue

    print("-" * 75)

    fig = plt.figure(figsize=(16, 10))

    ax1 = plt.subplot(2, 2, 1)

    markers = {'mid_rect': 'o', 'trapezoid': 's', 'simpson': '^', 'three_eighths': 'D',
               'gauss': 'p', 'radau': 'v', 'lobatto': '<', 'cheb': '>'}

    for r in results:
        method_type = r['method_type']
        marker = markers.get(method_type, 'o')
        ax1.scatter(r['time'], r['error'], s=120, c=r['color'],
                   marker=marker, alpha=0.7, edgecolors='black', linewidth=1)

    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.set_xlabel('Время вычисления, с', fontsize=11)
    ax1.set_ylabel('Абсолютная погрешность', fontsize=11)
    ax1.set_title('Диаграмма эффективности', fontsize=12)
    ax1.grid(True, alpha=0.3, which='both')

    ax2 = plt.subplot(2, 2, 2)

    for method_type, marker in markers.items():
        type_results = [r for r in results if r['method_type'] == method_type]
        if type_results:
            ns = [r['n'] for r in type_results]
            errs = [r['error'] for r in type_results]
            colors = [r['color'] for r in type_results]
            for n, err, col in zip(ns, errs, colors):
                ax2.scatter(n, err, s=80, c=col, marker=marker, alpha=0.7,
                           edgecolors='black', linewidth=1)

    ax2.set_xscale('log')
    ax2.set_yscale('log')
    ax2.set_xlabel('Число узлов/отрезков n', fontsize=11)
    ax2.set_ylabel('Абсолютная погрешность', fontsize=11)
    ax2.set_title('Зависимость точности от n', fontsize=12)
    ax2.grid(True, alpha=0.3, which='both')

    ax3 = plt.subplot(2, 2, 3)

    results_sorted = sorted(results, key=lambda x: x['efficiency'], reverse=True)[:12]

    methods_short = [r['method'].split('(')[0].strip() + f"\n(n={r['n']})" for r in results_sorted]
    efficiencies = [r['efficiency'] for r in results_sorted]
    colors = [r['color'] for r in results_sorted]

    max_eff = max(efficiencies)
    efficiencies_norm = [e/max_eff for e in efficiencies]

    bars = ax3.barh(range(len(methods_short)), efficiencies_norm, color=colors, alpha=0.7)
    ax3.set_yticks(range(len(methods_short)))
    ax3.set_yticklabels(methods_short, fontsize=9)
    ax3.set_xlabel('Относительная эффективность', fontsize=11)
    ax3.set_title('Топ-12 методов по эффективности', fontsize=12)
    ax3.grid(True, alpha=0.3, axis='x')

    ax4 = plt.subplot(2, 2, 4)
    ax4.axis('off')

    legend_text = """
    Типы методов и маркеры:
    
    o - Средние прямоугольники
    s - Метод трапеций
    ^ - Метод Симпсона
    D - Метод 3/8
    p - Гаусс-Лежандр
    v - Метод Радо
    < - Метод Лобатто
    > - Метод Чебышева
    """

    ax4.text(0.1, 0.9, legend_text, transform=ax4.transAxes, fontsize=10,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.suptitle(r'Рис. 2: Комплексный анализ эффективности методов' + '\n' +
                 r'$f(x) = e^{-x^2}$ на $[-2, 2]$', fontsize=14, y=1.02)
    plt.tight_layout()
    plt.savefig('efficiency_analysis.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("График сохранен: efficiency_analysis.png")

    return results

def analyze_special_cases():
    print("\n" + "="*70)
    print("АНАЛИЗ ПОВЕДЕНИЯ МЕТОДОВ НА ОСОБЫХ СЛУЧАЯХ")
    print("="*70)

    fig, axes = plt.subplots(2, 2, figsize=(14, 12))

    ax = axes[0, 0]
    f_runge = lambda x: 1 / (1 + 25 * x**2)
    a, b = -1, 1
    exact, _ = integrate.quad(f_runge, a, b)

    n_vals = np.arange(2, 17)

    methods_compare = {
        'Симпсон (Ньютон-Котес)': lambda n: simpson(f_runge, a, b, n if n%2==0 else n+1),
        'Гаусс-Лежандр': lambda n: gauss_legendre(f_runge, a, b, n),
        'Чебышев': lambda n: chebyshev(f_runge, a, b, min(n, 5)),
    }

    for label, method in methods_compare.items():
        errors = []
        ns_used = []
        for n in n_vals:
            try:
                I = method(n)
                if I is not None:
                    errors.append(max(abs(I - exact), 1e-16))
                    ns_used.append(n)
            except:
                pass
        if errors:
            ax.semilogy(ns_used, errors, 'o-', label=label, linewidth=2, markersize=4)

    ax.set_xlabel('Число узлов $n$', fontsize=11)
    ax.set_ylabel('Погрешность', fontsize=11)
    ax.set_title(r'Функция Рунге: $f(x)=1/(1+25x^2)$', fontsize=12)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    ax = axes[0, 1]
    f_step = lambda x: np.where(x < 0.5, 0.0, 1.0)
    a, b = 0, 1
    exact = 0.5

    methods_compare = {
        'Трапеции': lambda n: trapezoid(f_step, a, b, n),
        'Симпсон': lambda n: simpson(f_step, a, b, n),
        'Гаусс-2': lambda n: gauss_legendre(f_step, a, b, 2),
        'Гаусс-4': lambda n: gauss_legendre(f_step, a, b, 4),
    }

    for label, method in methods_compare.items():
        errors = []
        ns_used = []
        for n in [2, 4, 8, 16, 32, 64, 128]:
            try:
                I = method(n)
                errors.append(max(abs(I - exact), 1e-16))
                ns_used.append(n)
            except:
                pass
        if errors:
            ax.loglog(ns_used, errors, 'o-', label=label, markersize=4)

    ax.set_xlabel('$n$', fontsize=11)
    ax.set_ylabel('Погрешность', fontsize=11)
    ax.set_title('Ступенчатая функция', fontsize=12)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    ax = axes[1, 0]
    f_osc = lambda x: np.sin(10 * x)
    a, b = 0, np.pi
    exact = (1 - np.cos(10 * np.pi)) / 10

    for label, method in methods_compare.items():
        errors = []
        ns_used = []
        for n in [2, 4, 8, 16, 32, 64, 128, 256]:
            try:
                I = method(n)
                errors.append(max(abs(I - exact), 1e-16))
                ns_used.append(n)
            except:
                pass
        if errors:
            ax.loglog(ns_used, errors, 'o-', label=label, markersize=4)

    ax.set_xlabel('$n$', fontsize=11)
    ax.set_ylabel('Погрешность', fontsize=11)
    ax.set_title(r'$f(x)=\sin(10x)$', fontsize=12)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    ax = axes[1, 1]
    f_sing = lambda x: np.sqrt(x)
    a, b = 0, 1
    exact = 2/3

    methods_special = {
        'Средние прямоуг.': lambda n: mid_rect(f_sing, a, b, n),
        'Трапеции': lambda n: trapezoid(f_sing, a, b, n),
        'Гаусс-Лежандр': lambda n: gauss_legendre(f_sing, a, b, n),
        'Лобатто': lambda n: lobatto(f_sing, a, b, 4) if n==4 else None,
    }

    for label, method in methods_special.items():
        errors = []
        ns_used = []
        for n in [2, 4, 8, 16, 32, 64, 128]:
            try:
                I = method(n)
                if I is not None:
                    errors.append(max(abs(I - exact), 1e-16))
                    ns_used.append(n)
            except:
                pass
        if errors:
            ax.loglog(ns_used, errors, 'o-', label=label, markersize=4)

    ax.set_xlabel('$n$', fontsize=11)
    ax.set_ylabel('Погрешность', fontsize=11)
    ax.set_title(r'$f(x)=\sqrt{x}$ (особенность в $x=0$)', fontsize=12)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    plt.suptitle('Рис. 3: Поведение методов на особых случаях', fontsize=14, y=1.02)
    plt.tight_layout()
    plt.savefig('special_cases.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("График сохранен: special_cases.png")

def create_error_accumulation_plot():
    print("\n" + "="*70)
    print("АНАЛИЗ НАКОПЛЕНИЯ ПОГРЕШНОСТИ")
    print("="*70)

    fig, ax = plt.subplots(figsize=(12, 8))

    a = 0
    f = lambda t: t**2
    exact_integral = lambda x: x**3 / 3

    x_values = np.array([0.00, 0.02, 0.04, 0.06, 0.08, 0.10])

    methods = {
        'Трапеции': {'color': 'blue', 'marker': 's', 'offset': (5, 10)},
        'Симпсон': {'color': 'green', 'marker': '^', 'offset': (5, -20)},
        '3/8': {'color': 'red', 'marker': 'D', 'offset': (-40, 5)},
    }

    results = {}

    print(f"\n{'x':<8} {'Трапеции':<18} {'Симпсон':<18} {'3/8':<18}")
    print("-" * 65)

    for method_name in methods:
        errors = []
        for x in x_values:
            if x == 0:
                errors.append(0.0)
            else:
                b = x
                exact = exact_integral(b)
                n = 1000

                if method_name == 'Трапеции':
                    I = trapezoid(f, a, b, n)
                elif method_name == 'Симпсон':
                    n_simp = n if n % 2 == 0 else n + 1
                    I = simpson(f, a, b, n_simp)
                elif method_name == '3/8':
                    n_38 = n if n % 3 == 0 else ((n // 3) + 1) * 3
                    I = three_eighths(f, a, b, n_38)

                err = abs(I - exact)
                errors.append(err)

        results[method_name] = errors

    for i, x in enumerate(x_values):
        print(f"{x:<8.2f} ", end="")
        for method_name in methods:
            err = results[method_name][i]
            if err < 1e-15:
                print(f"{'< 1e-15':<18} ", end="")
            else:
                print(f"{err:<18.2e} ", end="")
        print()

    print("-" * 65)

    MIN_VISIBLE = 1e-18

    for method_name, method_data in methods.items():
        errors = results[method_name]
        errors_plot = [max(e, MIN_VISIBLE) for e in errors]

        ax.plot(x_values[1:], errors_plot[1:],
                color=method_data['color'],
                marker=method_data['marker'],
                linestyle='-',
                linewidth=2,
                markersize=10,
                label=method_name,
                markerfacecolor=method_data['color'],
                markeredgecolor='black',
                markeredgewidth=1.5)

    ax.set_yscale('log')
    ax.set_ylim(1e-18, 1e-1)

    ax.set_xlabel('Верхний предел интегрирования x', fontsize=12)
    ax.set_ylabel('Накопленная погрешность', fontsize=12)
    ax.set_title(r'Накопление погрешности численного интегрирования' + '\n' +
                 r'$f(t) = t^2$, $n = 1000$', fontsize=14)

    ax.grid(True, alpha=0.3, which='both')
    ax.legend(loc='lower right', fontsize=11)

    ax.axhline(y=1e-15, color='gray', linestyle='--', alpha=0.5, linewidth=1)
    ax.text(0.105, 2e-15, 'Уровень машинной точности', fontsize=9, alpha=0.6, ha='right')

    ax.text(0.5, 0.02,
            'Примечание: Симпсон и 3/8 дают точное значение для полинома 2-й степени',
            transform=ax.transAxes, fontsize=10, ha='center',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7))

    plt.tight_layout()
    plt.savefig('error_accumulation.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("График сохранен: error_accumulation.png")

    return results

def create_accuracy_vs_computation_plot():
    print("\n" + "="*70)
    print("АНАЛИЗ ВЛИЯНИЯ ТРЕБУЕМОЙ ТОЧНОСТИ НА ОБЪЕМ ВЫЧИСЛЕНИЙ")
    print("="*70)

    fig, ax = plt.subplots(figsize=(12, 8))

    epsilons = [1e-1, 1e-3, 1e-5, 1e-7, 1e-9, 1e-11, 1e-13, 1e-15, 1e-17]

    a, b = 0, 2
    f = lambda x: x**3 - 2*x**2 + x
    exact = (b**4/4 - 2*b**3/3 + b**2/2) - (a**4/4 - 2*a**3/3 + a**2/2)

    methods = {
        'Трапеции': {'color': 'blue', 'marker': 's', 'order': 2},
        'Прямоугольники': {'color': 'red', 'marker': 'o', 'order': 2},
        'Симпсон': {'color': 'green', 'marker': '^', 'order': 4},
        '3/8': {'color': 'purple', 'marker': 'D', 'order': 4},
    }

    epsilons_real = [1e-1, 1e-3, 1e-5, 1e-7]

    results = {method: [] for method in methods}

    print(f"\n{'Метод':<15} {'Точность':<12} {'n':<10} {'Факт. погрешность':<18}")
    print("-" * 60)

    for method_name, method_data in methods.items():
        for eps in epsilons_real:
            n = 2
            max_n = 50000
            found = False

            while n <= max_n:
                try:
                    if method_name == '3/8' and n < 3:
                        n += 1
                        continue
                    if method_name == 'Симпсон' and n % 2 != 0:
                        n += 1
                        continue

                    if method_name == 'Трапеции':
                        I = trapezoid(f, a, b, n)
                    elif method_name == 'Прямоугольники':
                        I = mid_rect(f, a, b, n)
                    elif method_name == 'Симпсон':
                        I = simpson(f, a, b, n)
                    elif method_name == '3/8':
                        I = three_eighths(f, a, b, n)

                    err = abs(I - exact)

                    if err < eps:
                        results[method_name].append((eps, n, err))
                        print(f"{method_name:<15} {eps:<12.0e} {n:<10} {err:<18.3e}")
                        found = True
                        break
                except:
                    pass
                n += 1

            if not found and len(results[method_name]) > 0:
                last_n = results[method_name][-1][1]
                last_eps = results[method_name][-1][0]

                if method_data['order'] == 2:
                    extrap_n = int(last_n * np.sqrt(last_eps / eps))
                else:
                    extrap_n = int(last_n * (last_eps / eps) ** 0.25)

                extrap_n = min(extrap_n, 1000000)
                results[method_name].append((eps, extrap_n, float('nan')))
                print(f"{method_name:<15} {eps:<12.0e} {extrap_n:<10} {'(экстраполяция)':<18}")

    print("-" * 60)

    for method_name, method_data in methods.items():
        eps_vals = [r[0] for r in results[method_name]]
        n_vals = [r[1] for r in results[method_name]]

        ax.loglog(eps_vals, n_vals,
                 color=method_data['color'],
                 marker=method_data['marker'],
                 label=method_name,
                 linewidth=2,
                 markersize=8,
                 markerfacecolor=method_data['color'],
                 markeredgecolor='black',
                 markeredgewidth=1)

        extrap_eps = [r[0] for r in results[method_name] if np.isnan(r[2])]
        extrap_n = [r[1] for r in results[method_name] if np.isnan(r[2])]

        if extrap_eps:
            ax.loglog(extrap_eps, extrap_n,
                     color=method_data['color'],
                     marker=method_data['marker'],
                     linestyle='--',
                     linewidth=1.5,
                     markersize=6,
                     markerfacecolor='none',
                     markeredgecolor=method_data['color'],
                     alpha=0.6)

    ax.set_xlabel(r'Требуемая точность $\varepsilon$', fontsize=12)
    ax.set_ylabel(r'Необходимое число разбиений $n$', fontsize=12)
    ax.set_title(r'Влияние требуемой точности на объем вычислений' + '\n' +
                 r'$f(x) = x^3 - 2x^2 + x$ на $[0, 2]$', fontsize=14)

    ax.invert_xaxis()

    for eps in epsilons:
        ax.axvline(x=eps, color='gray', linestyle=':', alpha=0.3, linewidth=0.5)

    ax2 = ax.twiny()
    ax2.set_xscale('log')
    ax2.set_xlim(ax.get_xlim())
    ax2.set_xticks(epsilons)
    ax2.set_xticklabels([f'$10^{{{int(np.log10(e))}}}$' for e in epsilons], fontsize=9, rotation=45)
    ax2.set_xlabel(r'Границы точности', fontsize=11)
    ax2.invert_xaxis()

    ax.grid(True, alpha=0.3, which='both')

    legend_elements = []
    for method_name, method_data in methods.items():
        legend_elements.append(plt.Line2D([0], [0], color=method_data['color'],
                                         marker=method_data['marker'], linewidth=2,
                                         markerfacecolor=method_data['color'],
                                         markeredgecolor='black',
                                         label=method_name))
    legend_elements.append(plt.Line2D([0], [0], color='gray', linestyle='--',
                                     linewidth=1.5, label='Экстраполяция'))

    ax.legend(handles=legend_elements, loc='lower left', fontsize=10)

    plt.tight_layout()
    plt.savefig('accuracy_vs_computation.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("График сохранен: accuracy_vs_computation.png")

    return results

def print_summary_table():
    print("\n" + "="*70)
    print("СВОДНАЯ ТАБЛИЦА ХАРАКТЕРИСТИК КВАДРАТУРНЫХ ФОРМУЛ")
    print("="*70)

    summary = [
        {'name': 'Левые прямоуг.', 'order': 1, 'alg_acc': 0, 'type': 'Ньютон-Котес', 'nodes': 'равноотстоящие'},
        {'name': 'Средние прямоуг.', 'order': 2, 'alg_acc': 1, 'type': 'Ньютон-Котес', 'nodes': 'равноотстоящие'},
        {'name': 'Трапеции', 'order': 2, 'alg_acc': 1, 'type': 'Ньютон-Котес', 'nodes': 'равноотстоящие'},
        {'name': 'Симпсон', 'order': 4, 'alg_acc': 3, 'type': 'Ньютон-Котес', 'nodes': 'равноотстоящие'},
        {'name': '3/8', 'order': 4, 'alg_acc': 3, 'type': 'Ньютон-Котес', 'nodes': 'равноотстоящие'},
        {'name': 'Гаусс-Лежандр (n=2)', 'order': 4, 'alg_acc': 3, 'type': 'Гаусс', 'nodes': 'оптимальные'},
        {'name': 'Гаусс-Лежандр (n=3)', 'order': 6, 'alg_acc': 5, 'type': 'Гаусс', 'nodes': 'оптимальные'},
        {'name': 'Гаусс-Лежандр (n=4)', 'order': 8, 'alg_acc': 7, 'type': 'Гаусс', 'nodes': 'оптимальные'},
        {'name': 'Радо (левый, n=2)', 'order': 3, 'alg_acc': 2, 'type': 'Гаусс-Радо', 'nodes': 'вкл. лев. границу'},
        {'name': 'Радо (правый, n=2)', 'order': 3, 'alg_acc': 2, 'type': 'Гаусс-Радо', 'nodes': 'вкл. прав. границу'},
        {'name': 'Лобатто (n=3)', 'order': 4, 'alg_acc': 3, 'type': 'Гаусс-Лобатто', 'nodes': 'вкл. обе границы'},
        {'name': 'Лобатто (n=4)', 'order': 6, 'alg_acc': 5, 'type': 'Гаусс-Лобатто', 'nodes': 'вкл. обе границы'},
        {'name': 'Чебышев (n=2)', 'order': 3, 'alg_acc': 2, 'type': 'Чебышев', 'nodes': 'равные веса'},
        {'name': 'Чебышев (n=3)', 'order': 3, 'alg_acc': 3, 'type': 'Чебышев', 'nodes': 'равные веса'},
    ]

    print(f"\n{'Метод':<25} {'Порядок':<10} {'Алг. точн.':<12} {'Тип':<18} {'Узлы':<20}")
    print("-" * 90)
    for s in summary:
        print(f"{s['name']:<25} {s['order']:<10} {s['alg_acc']:<12} {s['type']:<18} {s['nodes']:<20}")
    print("-" * 90)

def main():
    print("="*70)
    print("РАСЧЕТНО-ГРАФИЧЕСКАЯ РАБОТА №2")
    print("КВАДРАТУРНЫЕ ФОРМУЛЫ ГАУССА И СМЕШАННОГО ТИПА")
    print("="*70)
    print("Выполнил: Джангулов Григорий Маратович")
    print("Группа: 13.2")
    print("="*70)

    if not scare_user():
        print("Программа завершена из-за отказа пользователя.")
        return

    test_algebraic_accuracy()
    study_convergence_extended()
    efficiency_analysis()
    analyze_special_cases()
    create_error_accumulation_plot()
    create_accuracy_vs_computation_plot()
    print_summary_table()

    print("\n" + "="*70)
    print("ВЫЧИСЛЕНИЯ ЗАВЕРШЕНЫ УСПЕШНО")
    print("="*70)
    print("Сохраненные файлы:")
    print("  - convergence_extended.png")
    print("  - efficiency_analysis.png")
    print("  - special_cases.png")
    print("  - error_accumulation.png")
    print("  - accuracy_vs_computation.png")
    print("="*70)
    print("\nСпасибо за работу! Ваш компьютер в безопасности.")
    print("На этот раз...")

if __name__ == "__main__":
    main()