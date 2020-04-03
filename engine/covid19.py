import random


def calc(N, n, T, nG, home_infect, each, DAYoff, n_key, lim):

    perc = []
    off_perc = []
    home_infect = 1.5 #  INPUT PARAM4

    for i in range(nG):
        perc.append(each[i])
        off_perc.append(home_infect)

    off=[]
    for i in range(nG):
        off.append(DAYoff[i])

    person = [[] for x in range(N)] #2d list of all staff members, with their avaialibilty over the time period
    group = [[] for x in range(N)] #Corresponding list to show what AREA each staff member is in on each day

    infection_day = [0 for x in range(N)] #The day each staff member is infected
    incub_store = [0 for x in range(N)]
    groups = ['AREA 1', 'AREA 2', 'AREA 3', 'AREA 4', 'AREA 5', 'AREA 6', 'AREA 7', 'AREA 8']
    time_off = ['off 1', 'off 2', 'off 3', 'off 4', 'off 5', 'off 6', 'off 7', 'off 8']
    incubation = [2, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 8, 8, 8, 9, 9, 10, 11, 12]
    def when_infect(p, p_off):
        infect = -100
        start = 0

        for a in range(int(T/(n*nG))):
            for b in range(nG):
                if(infect<0):
                    for i in range(start*n, (start+1)*n - off[b]):
                        if (random.randint(0,100) < p[b]):
                            if(infect<0):
                                   infect = i
                    for i in range((start+1)*n - off[b], (start+1)*n):
                        if (random.randint(0,100) < p_off[b]):
                            if(infect<0):
                                   infect = i
                start+=1

        return(infect)


    for a in range(N): #Loop through all staff able to work across all areas
        for X in range(nG):
            if((a>=X*N/nG) & (a<(X+1)*N/nG)): #First section of staff start shift in area 1
                for b in range(int(T/n*nG)):
                    for c in range(X, nG):
                        for j in range(n-off[c]):
                            group[a].append(groups[c])
                        for j in range(off[c]):
                            group[a].append(time_off[c])
                    for c in range(0, X):
                        for j in range(n-off[c]):
                            group[a].append(groups[c])
                        for j in range(off[c]):
                            group[a].append(time_off[c])
                p = []
                for i in range(X, nG):
                    p.append(perc[i])
                for i in range(0, X):
                    p.append(perc[i])
                p_off = []

                for i in range(X, nG):
                    p_off.append(off_perc[i])
                for i in range(0, X):
                    p_off.append(off_perc[i])
                infect = when_infect(p, p_off)


                if(infect>=0):
                        infection_day[a] = infect
                        inc = 0.17 / 28
                        r = random.randint(0,len(incubation) -1)
                        incub = incubation[r]
                        incub_store[a] = incub
                        for k in range(infect+incub): #available to work until day of infection plus 5 day incubation period
                            person[a].append(1)
                        for k in range(14):
                            person[a].append(0) #unavailable to work for 14 days while symptomatic / in isolation
                        for k in range(28):
                            person[a].append(0.8 +k*inc) #2 weeks following symptoms 80% of staff return. In following 4 weeks the remainder gradually return
                        for k in range(T - 42 - (infect+incub)):
                            person[a].append(0.97) #6 weeks after symptoms 97% of staff have returned

                if(infect<0):
                    infection_day[a] = 'never'
                    for k in range(T):
                        person[a].append(1)


    def column(matrix, i):
        return [row[i] for row in matrix]

    day = []
    total = []
    total_col = [[] for x in range(nG)]
    total_off = [[] for x in range(nG)]
    total_col_plot = [[] for x in range(nG)]
    id_col = [[] for x in range(nG)]
    id_off = [[] for x in range(nG)]
    amount_col = [[] for x in range(nG)]
    amount_off = [[] for x in range(nG)]

    col_g = [0 for x in range(T)]

    for j in range(T):
        day.append(j+1)
        day.append(j+2)
        col = column(person, j) #List of available people on day j

        sum_col=0
        for x in range(len(col)):
            sum_col+=col[x]
        col_g[j] = column(group, j) #List of area distribution on day j
        total.append(sum_col) #Total number of staff available on day j
        total.append(sum_col)

        add_col = [0 for x in range(nG)]
        add_off = [0 for x in range(nG)]
        who_col = [[] for x in range(nG)]
        who_off = [[] for x in range(nG)]
        am_col = [[] for x in range(nG)]
        am_off = [[] for x in range(nG)]


        for k in range(len(col)):
            for a in range(nG):
                if(col_g[j][k] == groups[a]):
                     add_col[a]+=col[k]
                     who_col[a].append(k)
                     am_col[a].append(col[k])
                if(col_g[j][k] == time_off[a]):
                     add_off[a]+=col[k]
                     who_off[a].append(k)
                     am_off[a].append(col[k])

        for a in range(nG):
            total_col[a].append(add_col[a]) #Available staff working in specific area
            for b in range(2):
                total_col_plot[a].append(add_col[a] + add_off[a])
            total_off[a].append(add_off[a]) #Available staff off work in specific area
            id_col[a].append(who_col[a]) #List of which staff in specific area
            id_off[a].append(who_off[a]) #List of which staff having days off in specific area
            amount_col[a].append(am_col[a])
            amount_off[a].append(am_off[a])

    if n_key is None:
        return day, total, total_col_plot

    else:

        for y in range(T):
             if(y>0):

                 if((total_col[n_key-1][y]<lim) and (total_off[n_key-1][y]==0)):


                     sum = 0
                     num = lim-total_col[n_key-1][y]


                     other = [-100 for x in range(2*nG)]
                     other_id = [-100 for x in range(2*nG)]
                     other_am = [-100 for x in range(2*nG)]

                     for l in range(nG):
                         if (l!=(n_key-1)):
                                 other[l] = (total_off[l][y])
                                 other_id[l] = (id_off[l][y])
                                 other_am[l] = (amount_off[l][y])

                     for l in range(nG):
                         if (l!=(n_key-1)):
                             other[l+nG] = (total_col[l][y])
                             other_id[l+nG] = (id_col[l][y])
                             other_am[l+nG] = (amount_col[l][y])

                     save_by = []
                     saver = []
                     for x in range(len(other)):
                        if(other[x]>0):
                            for z in range(len(other_am[x])):

                                person[other_id[x][z]][y]-=other_am[x][z]
                                if(len(id_col[n_key-1][y])==0):
                                    id_col[n_key-1][y].append(0)
                                person[id_col[n_key-1][y][0]][y]+=other_am[x][z]
                                sum+=other_am[x][z]

                                save_by.append(other_am[x][z])
                                saver.append(other_id[x][z])
                                if sum>= num:
                                    break

                        if sum>= num:
                            break


                     for x in range(len(saver)):
                        if(infection_day[saver[x]]!='never'):
                            if(y < infection_day[saver[x]]):

                                if (random.randint(0,100) < perc[n_key-1]):
                                    incub = incub_store[saver[x]]
                                    inc = 0.17 / 28
                                    for k in range(1, incub):
                                        if((k+y)<T):
                                                person[saver[x]][k+y] = 1
                                    for k in range(incub, incub+14):
                                        if((k+y)<T):
                                                person[saver[x]][k+y]=0

                                    for k in range(incub + 14, incub + 42):
                                        if((k+y)<T):
                                                person[saver[x]][k+y]= 0.8 + (k - (incub + 14))*inc
                                    for k in range(y + incub + 42, T):
                                                person[saver[x]][k]= 0.97

                        else:
                            if (random.randint(0,100) < perc[n_key-1]):
                                incub = incub_store[saver[x]]
                                inc = 0.17 / 28
                                for k in range(1, incub):
                                    if((k+y)<T):
                                            person[saver[x]][k+y] = 1
                                for k in range(incub, incub+14):
                                    if((k+y)<T):
                                            person[saver[x]][k+y]=0

                                for k in range(incub + 14, incub + 42):
                                    if((k+y)<T):
                                            person[saver[x]][k+y]= 0.8 + (k - (incub + 14))*inc
                                for k in range(y + incub + 42, T):
                                            person[saver[x]][k]= 0.97


                     total_col = [[] for x in range(nG)]
                     total_off = [[] for x in range(nG)]
                     total_col_plot = [[] for x in range(nG)]
                     id_col = [[] for x in range(nG)]
                     id_off = [[] for x in range(nG)]
                     amount_col = [[] for x in range(nG)]
                     amount_off = [[] for x in range(nG)]
                     for j in range(T):
                            col = column(person, j) #List of available people on day j


                            add_col = [0 for x in range(nG)]
                            add_off = [0 for x in range(nG)]
                            who_col = [[] for x in range(nG)]
                            who_off = [[] for x in range(nG)]
                            am_col = [[] for x in range(nG)]
                            am_off = [[] for x in range(nG)]

                            for k in range(len(col)):
                                for a in range(nG):
                                    if(col_g[j][k] == groups[a]):
                                         add_col[a]+=col[k]
                                         who_col[a].append(k)
                                         am_col[a].append(col[k])
                                    if(col_g[j][k] == time_off[a]):
                                         add_off[a]+=col[k]
                                         who_off[a].append(k)
                                         am_off[a].append(col[k])

                            for a in range(nG):
                                total_col[a].append(add_col[a]) #Available staff working in specific AREA
                                total_off[a].append(add_off[a]) #Available staff off work in specific AREA
                                id_col[a].append(who_col[a]) #List of which staff in specific AREA
                                id_off[a].append(who_off[a]) #List of which staff having days off in specific AREA
                                amount_col[a].append(am_col[a])
                                amount_off[a].append(am_off[a])


        person2 = [[0 for y in range(T)] for x in range(N)]

        for x in range(N):
            for y in range(T):
                person2[x][y] = person[x][y]


        total2 = []
        total_col_plot2 = [[] for x in range(nG)]
        for j in range(T):
            col = column(person2, j) #List of available people on day j
            sum_col=0
            for x in range(len(col)):
                sum_col+=col[x]
            col_g[j] = column(group, j) #List of AREA distribution on day j
            total2.append(sum_col) #Total number of staff available on day j
            total2.append(sum_col)

            add_col = [0 for x in range(nG)]
            add_off = [0 for x in range(nG)]


            for k in range(len(col)):
                for a in range(nG):
                    if(col_g[j][k] == groups[a]):
                         add_col[a]+=col[k]

                    if(col_g[j][k] == time_off[a]):
                         add_off[a]+=col[k]

            for a in range(nG):
                for b in range(2):
                    total_col_plot2[a].append(add_col[a] + add_off[a])

        return day, total2, total_col_plot2
