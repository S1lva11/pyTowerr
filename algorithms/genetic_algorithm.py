import time
import settings
import random

""" Implementação de um Algoritmo Genético que permite melhorar o desempenho de disparo (performance de ataque) das torres """

class GeneticAlgorithm:
    def __init__(self, tower_type):
        self.num_generations = 40
        self.fitness_threshold = 0.9
        self.num_genes = 4  # accuracy, cooldown, range, firepower
        self.population_size = 20 # número de torres
        self.tower_type = tower_type
        self.population = self.initialize_population()
        self.current_generation = 0

    def initialize_population(self):
        """
        Initialize the population with random values
        :return: list of lists, each containing the genes for an individual
        """
        # Obter intervalos para este tipo de torre a partir das settings
        accuracy_min, accuracy_max = 0.01, 1.0 # varia entre 0.01 a 1.0
        cooldown_min, cooldown_max = settings.TOWER_TYPES[self.tower_type]['cooldown'] # varia entre 100 ms a 4000 ms
        range_min, range_max = settings.TOWER_TYPES[self.tower_type]['range'] # varia entre 50 a 100 unidades
        damage_min, damage_max = settings.TOWER_TYPES[self.tower_type]['damage'] # varia entre 1 a 3 pontos de dano 

        first_population = []

        for i in range(self.population_size):
            # Inicialização aleatória dos valores de cada gene
            accuracy = round(random.uniform( accuracy_min, accuracy_max ),2) # (inclui números decimais)
            cooldown = random.randint(cooldown_min, cooldown_max) # (inclui números inteiros)
            range_ = random.randint(range_min, range_max)
            damage = random.randint(damage_min, damage_max)

            first_population.append([accuracy, cooldown, range_, damage])

        print("População iniciada: ", first_population)
        return first_population

    def fitness_function(self, individual):
        """
        Calculate the fitness score for an individual
        :param individual: list of genes for an individual
        :return: float, the fitness score, between 0 and 1
        """
        accuracy, cooldown, range_, damage = individual # obter genes da torre
        
        # função de avaliação fitness (Atribuir scores (importância) para cada gene) 
        score_accuracy = 1.5
        score_cooldown = 2
        score_range = 1
        score_damage = 1

        # Normalizar os valores para o intervalo entre 0 e 1
        normalized_accuracy = accuracy  # já está entre 0 e 1
        normalized_cooldown = (4000 - cooldown) / 3900  # inverter para que menor seja melhor
        normalized_range = (range_ - 50) / 50
        normalized_damage = (damage - 1) / 2  

        # Calcular e normalizar o fitness ponderado
        fitness = (
            score_accuracy * normalized_accuracy +
            score_cooldown * normalized_cooldown +
            score_range * normalized_range +
            score_damage * normalized_damage
        )

        # Normalizar pelo total dos scores
        total_score = score_accuracy + score_cooldown + score_range + score_damage
        fitness /= total_score # fitness = fitness / total_score

        fitness = round(fitness,2) # arredondar para 2 casas decimais
        
        print(fitness)
        return (fitness)

    def run_generation(self):
        """
        Run a single generation of the genetic algorithm
        This is where the selection, crossover, and mutation steps are performed
        """
         # Calcular fitness para a população atual
        fitness_scores = [self.fitness_function(ind) for ind in self.population]
        sorted_population = [ind for _, ind in sorted(zip(fitness_scores, self.population), reverse=True)]
        
        # Selecionar os 50% melhores indivíduos como pais
        num_parents = self.population_size // 2
        parents = sorted_population[:num_parents]

        next_generation = parents.copy() # Iniciar a próxima geração com os pais
        
        # Gerar a próxima geração com crossover e mutação para cada indivíduo
        while len(next_generation) < self.population_size:
            parent1, parent2 = random.sample(parents, 2) # Selecionar dois pais aleatórios
            child1, child2 = self.crossover(parent1, parent2)  # Gerar dois filhos com crossover
            next_generation.append(self.mutate(child1))  # Mutar e adicionar o primeiro filho
            if len(next_generation) < self.population_size:
                next_generation.append(self.mutate(child2))  # Mutar e adicionar o segundo filho (se a próxima geração não ultrapassar o tamanho da população (10))

        self.population = next_generation

    def crossover(self, parent1, parent2):
        """
        Perform crossover between two parents to produce a child
        :param parent1: Invividual 1 to crossover
        :param parent2: Individual 2 to crossover
        :return: list, the genes of the child (individual)
        """

        # Selecionar dois pontos de corte aleatórios
        point1 = random.randint(1, self.num_genes - 2)  # Ponto de corte 1
        point2 = random.randint(point1 + 1, self.num_genes - 1)  # Ponto de corte 2

        # Criar o primeiro filho misturando os genes dos pais
        child1 = (
            parent1[:point1] +        # Segmento 1 do Pai 1
            parent2[point1:point2] +  # Segmento 2 do Pai 2
            parent1[point2:]          # Segmento 3 do Pai 1
        )

        # Criar o segundo filho invertendo os segmentos de genes dos pais
        child2 = (
            parent2[:point1] +        # Segmento 1 do Pai 2
            parent1[point1:point2] +  # Segmento 2 do Pai 1
            parent2[point2:]          # Segmento 3 do Pai 2
        )

        return child1, child2 # retorna os dois filhos
    
    def mutate(self, individual):
        """
        Perform mutation on an individual
        :param individual: list, the genes of the individual to mutate
        :return: list, the genes of the mutated individual
        """
        mutation_rate = 0.25  # 25% probabilidade de mutação
        chance = random.random()

        # mutação uniforme
        for i in range(len(individual)):
            if chance < mutation_rate: # verifica se a chance aleatória está dentro dos 10% de chance de mutação
                # obter valores min e max para cada gene
                range_min, range_max = settings.TOWER_TYPES[self.tower_type]['range']
                cooldown_min, cooldown_max = settings.TOWER_TYPES[self.tower_type]['cooldown']
                damage_min, damage_max = settings.TOWER_TYPES[self.tower_type]['damage']

                # mutar o valor de cada gene
                if i == 0:  # Accuracy
                    individual[i] = round(random.uniform(0.1, 1.0),2)
                elif i == 1:  # Cooldown
                    individual[i] = random.randint(cooldown_min, cooldown_max)
                elif i == 2:  # Range
                    individual[i] = random.randint(range_min, range_max)
                elif i == 3:  # Damage
                    individual[i] = random.randint(damage_min, damage_max)

        return individual

    def get_best_solution(self, num_solutions=1):
        """
        Get the best solution(s) from the final generation
        :param num_solutions: int, the number of best solutions to return (default is 1). Use 6 for the final solution
        :return: list of lists, the best solution(s) from the final generation. It should return 6 solutions for the 6 towers
        """
        # Calcular fitness para a população atual
        fitness_scores = [self.fitness_function(ind) for ind in self.population]

        # Ordenar a população por fitness
        sorted_population = sorted(
            zip(fitness_scores, self.population), # agrupar fitness e indivíduos (fitness, individuo)
            key=lambda x: x[0], # definir um critério de ordenação (ordenar pelo fitness)
            reverse=True # ordena do maior para o menor
        )

        top_solutions = [ind for _, ind in sorted_population[:num_solutions]] # Obter os melhores indivíduos
        top_fitnesses = [score for score, _ in sorted_population[:num_solutions]] # Obter os melhores fitness scores

        return top_solutions, top_fitnesses

    def get_current_generation(self):
        """
        Get the current generation number
        :return: int, the current generation number
        """
        return self.current_generation

    # def run(self):
    #     """
    #     Run the genetic algorithm for the specified number of generations.
    #     It uses the run_generation method to perform the steps for each generation
    #     """
    #     for i in range(self.num_generations):
    #         self.current_generation = i + 1
    #         self.run_generation()

    # def run(self):
    #     """
    #     Run the genetic algorithm for the specified number of generations.
    #     Stops if the average fitness score of the population >= 0.85, or runs up to the max number of generations.
    #     """
    #     target_fitness = 0.85  # Define o objetivo para a média do fitness
    #     for i in range(self.num_generations):
    #         self.current_generation = i + 1
    #         self.run_generation()

    #         # Calcular a média do fitness da população atual
    #         fitness_scores = [self.fitness_function(ind) for ind in self.population]
    #         average_fitness = sum(fitness_scores) / len(fitness_scores)

    #         print(f"Geração {self.current_generation}, Média de Fitness: {average_fitness:.4f}")

    #         # Parar se a média do fitness atingir ou exceder o objetivo
    #         if average_fitness >= target_fitness:
    #             print(f"Objetivo de média de fitness alcançado na geração {self.current_generation}!")
    #             break

    def run(self):
        """
        Run the genetic algorithm for the specified number of generations.
        Stops if the average fitness score of the population >= 0.9 (until fitness threshold is reached), or the max number of generations is completed.
        """
        start_time = time.time()
        
        while self.current_generation < self.num_generations:
            self.current_generation += 1
            self.run_generation()
            
            # Calcular a média do fitness score para a população atual
            fitness_scores = (self.fitness_function(ind) for ind in self.population)
            avg_fitness = sum(fitness_scores) / len(self.population)

            print(f"Geração {self.current_generation}, Média de Fitness: {avg_fitness:.4f}")
            
            # Parar se a média do fitness score atingir ou exceder o objetivo
            if avg_fitness >= self.fitness_threshold:
                print(f"Objetivo de média de fitness alcançado na geração {self.current_generation}!")
                break
        
        end_time = time.time()
        delta_time = end_time - start_time
        
        print(f"Duração {delta_time} segundos para gerar {self.current_generation} gerações.")


