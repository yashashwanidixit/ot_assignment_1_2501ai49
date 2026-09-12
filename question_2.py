import sys


sys.setrecursionlimit(2000)

class TransportationSolver:
    def __init__(self, costs, supply, demand):
       
        self.original_costs = [row[:] for row in costs]
        self.costs = [row[:] for row in costs]
        self.supply = supply[:]
        self.demand = demand[:]
        self.rows = len(supply)
        self.cols = len(demand)
        self.allocation = [[0] * self.cols for _ in range(self.rows)]
   
        total_supply = sum(self.supply)
        total_demand = sum(self.demand)
        
        if total_supply != total_demand:
            print(f"\nSupply: {total_supply}, Demand: {total_demand})")
            self._balance_problem(total_supply, total_demand)

    def _balance_problem(self, total_supply, total_demand):
      
        if total_supply > total_demand:
            diff = total_supply - total_demand
            self.demand.append(diff)
            for r in range(self.rows):
                self.costs[r].append(0)
            self.cols += 1
        else:
            diff = total_demand - total_supply
            self.supply.append(diff)
            self.costs.append([0] * self.cols)
            self.rows += 1
   
        self.allocation = [[0] * self.cols for _ in range(self.rows)]

    def solve(self):
       
   
        self._run_vam()
        current_cost = self._calculate_total_cost()
        self._print_matrix("initial basic feasible solution", current_cost)

 
        iteration = 1
        while True:
       
            is_optimal, deltas, u, v = self._modi_check_optimality()
            
            if is_optimal:
                print("optimal solution found ")
                break

     
            min_delta = float('inf')
            enter_i, enter_j = -1, -1
            
            for i in range(self.rows):
                for j in range(self.cols):
               
                    if self.allocation[i][j] == 0 and deltas[i][j] < min_delta:
                        min_delta = deltas[i][j]
                        enter_i, enter_j = i, j

            print(f"iteration {iteration}: cell ({enter_i+1},{enter_j+1}) enters basis (delta={min_delta}).")
            
     
            self._perform_stepping_stone(enter_i, enter_j)
            
            current_cost = self._calculate_total_cost()
            self._print_matrix(f"after iteration {iteration}", current_cost)
            iteration += 1

        return self.allocation, current_cost

    def _run_vam(self):
        
        temp_supply = self.supply[:]
        temp_demand = self.demand[:]
        temp_costs = [row[:] for row in self.costs]
        alloc = [[0] * self.cols for _ in range(self.rows)]

        while sum(temp_supply) > 0:
       
            row_penalties = []
            for r in range(self.rows):
                if temp_supply[r] == 0:
                    row_penalties.append(-1)
                    continue
               
                active_costs = [temp_costs[r][c] for c in range(self.cols) if temp_demand[c] > 0]
                if len(active_costs) >= 2:
                    sorted_costs = sorted(active_costs)
                    row_penalties.append(sorted_costs[1] - sorted_costs[0])
                elif len(active_costs) == 1:
                    row_penalties.append(active_costs[0])
                else:
                    row_penalties.append(-1)

            col_penalties = []
            for c in range(self.cols):
                if temp_demand[c] == 0:
                    col_penalties.append(-1)
                    continue
                active_costs = [temp_costs[r][c] for r in range(self.rows) if temp_supply[r] > 0]
                if len(active_costs) >= 2:
                    sorted_costs = sorted(active_costs)
                    col_penalties.append(sorted_costs[1] - sorted_costs[0])
                elif len(active_costs) == 1:
                    col_penalties.append(active_costs[0])
                else:
                    col_penalties.append(-1)

   
            max_rp = max(row_penalties) if row_penalties else -1
            max_cp = max(col_penalties) if col_penalties else -1
            
            target_r, target_c = -1, -1
            select_row = True 

            if max_rp >= max_cp:
                select_row = True
                target_r = row_penalties.index(max_rp)
            else:
                select_row = False
                target_c = col_penalties.index(max_cp)


            if select_row:
     
                min_val = float('inf')
                min_c = -1
                for c in range(self.cols):
                    if temp_demand[c] > 0 and temp_costs[target_r][c] < min_val:
                        min_val = temp_costs[target_r][c]
                        min_c = c
               
                qty = min(temp_supply[target_r], temp_demand[min_c])
                alloc[target_r][min_c] = qty
                temp_supply[target_r] -= qty
                temp_demand[min_c] -= qty
            else:
              
                min_val = float('inf')
                min_r = -1
                for r in range(self.rows):
                    if temp_supply[r] > 0 and temp_costs[r][target_c] < min_val:
                        min_val = temp_costs[r][target_c]
                        min_r = r
                
                qty = min(temp_supply[min_r], temp_demand[target_c])
                alloc[min_r][target_c] = qty
                temp_supply[min_r] -= qty
                temp_demand[target_c] -= qty

        self.allocation = alloc

    def _get_basic_cells(self):

        basics = []
        for i in range(self.rows):
            for j in range(self.cols):
                if self.allocation[i][j] != 0:
                    basics.append((i, j))
        return basics

    def _modi_check_optimality(self):
       
        basics = self._get_basic_cells()
        required_num_basics = self.rows + self.cols - 1

        if len(basics) < required_num_basics:
            self._handle_degeneracy(basics, required_num_basics)
            basics = self._get_basic_cells() 

        u = [None] * self.rows
        v = [None] * self.cols
        u[0] = 0 

   
        changed = True
        iterations = 0
        while changed and iterations < 1000:
            changed = False
            iterations += 1
            for (r, c) in basics:
                if u[r] is None and v[c] is not None:
                    u[r] = self.costs[r][c] - v[c]
                    changed = True
                elif v[c] is None and u[r] is not None:
                    v[c] = self.costs[r][c] - u[r]
                    changed = True
        
   
        deltas = [[0]*self.cols for _ in range(self.rows)]
        is_optimal = True
        for r in range(self.rows):
            for c in range(self.cols):
                if (r,c) not in basics:
                    deltas[r][c] = self.costs[r][c] - (u[r] + v[c])
                    if deltas[r][c] < 0:
                        is_optimal = False
                        
        return is_optimal, deltas, u, v

    def _handle_degeneracy(self, current_basics, required):

        count_needed = required - len(current_basics)
        if count_needed <= 0: return
        
      
        added = 0
        for i in range(self.rows):
            for j in range(self.cols):
                if added >= count_needed: return
                if self.allocation[i][j] == 0:
                    self.allocation[i][j] = 0 
                    added += 1

    def _perform_stepping_stone(self, enter_r, enter_c):

        
        path = []

        
     
        found_loop = [False]
        loop_path = []

        def search(r, c, came_from, curr_path):
            if found_loop[0]: return
        
            if r == enter_r and c == enter_c and len(curr_path) > 0:
                found_loop[0] = True
                loop_path.extend(curr_path)
                return

      
            if (r, c) in [(p[0], p[1]) for p in curr_path]: return

        
            
            if came_from == 'ROW' or came_from == 'START':
          
                for n_r in range(self.rows):
                    if n_r == r: continue
                    if self.allocation[n_r][c] != 0: 
                        search(n_r, c, 'COL', curr_path + [(n_r, c)])
            
            if came_from == 'COL' or came_from == 'START':
          
                for n_c in range(self.cols):
                    if n_c == c: continue
                    if self.allocation[r][n_c] != 0: 
                        search(r, n_c, 'ROW', curr_path + [(r, n_c)])

 
        started = False
        for k in range(self.cols):
            if k != enter_c and self.allocation[enter_r][k] != 0:
                search(enter_r, k, 'ROW', [(enter_r, k)])
                started = True
                break
        
        if not found_loop[0]:
           
            for k in range(self.rows):
                if k != enter_r and self.allocation[k][enter_c] != 0:
                    search(k, enter_c, 'COL', [(k, enter_c)])
                    break

        if not found_loop[0]:
            print(f"Error: Could not find closed loop for ({enter_r},{enter_c})")
            return

     
        
        min_qty = float('inf')
        subtract_indices = [] 
        
        for i in range(len(loop_path)):
            if i % 2 == 0:
                r, c = loop_path[i]
                val = self.allocation[r][c]
                if val < min_qty:
                    min_qty = val
        
        theta = min_qty

        self.allocation[enter_r][enter_c] += theta
        
        for i in range(len(loop_path)):
            r, c = loop_path[i]
            if i % 2 == 0:
                self.allocation[r][c] -= theta
            else: 
                self.allocation[r][c] += theta
                
    
        for i in range(self.rows):
            for j in range(self.cols):
                if abs(self.allocation[i][j]) < 1e-9:
                    self.allocation[i][j] = 0

    def _calculate_total_cost(self):
        total = 0
        for i in range(self.rows):
            for j in range(self.cols):
                total += self.allocation[i][j] * self.costs[i][j]
        return total

    def _print_matrix(self, title, total_cost):
 
        header = " " * 12 + "".join([f"D{j+1:<10}" for j in range(self.cols)]) + "Supply"
        print(header)
        for i in range(self.rows):
            row_str = f"S{i+1:<12}"
            for j in range(self.cols):
                val = self.allocation[i][j]
                if val > 0:
                    row_str += f"{val:<10}"
                else:
                    row_str += "-         "
            row_str += str(self.supply[i])
            print(row_str)
            
        footer = " " * 12 + "".join([f"{self.demand[j]:<10}" for j in range(self.cols)])
        print(footer)
        print(f"Total Cost: {total_cost}")



if __name__ == "__main__":
    
    costs_data = [
        [3, 1, 7, 4],
        [2, 6, 5, 9],
        [8, 3, 3, 2]
    ]
    
    supply_data = [300, 400, 500]
    demand_data = [250, 350, 400, 200]

    try:
        solver = TransportationSolver(costs_data, supply_data, demand_data)
        final_alloc, min_cost = solver.solve()

        print(f"minimum cost: {min_cost}")

        
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()