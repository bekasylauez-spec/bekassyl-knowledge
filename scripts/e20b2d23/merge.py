import fitz,sys
D='C:/Users/Admin/Downloads/'
sel=[('КДС-2026-1-04.01-АР.pdf','АБК',[(8,'План 1 этажа на отм. 0,000'),(14,'Разрез 1-1'),(15,'Разрез 2-2')]),
 ('КДС-2026-1-05.01-АР.pdf','Пожарный пост на 2 автомобиля',[(9,'План 1 этажа на отм. 0,000'),(13,'Разрез 1-1'),(14,'Разрез 2-2'),(15,'Разрез 3-3')]),
 ('КДС-2026-1-06.01-АР.pdf','КПП №1 с въездной аркой',[(7,'План на отм. 0,000'),(8,'Разрезы 1-1, 2-2, 3-3')]),
 ('КДС-2026-1-07.01-АС.pdf','КПП №2 модульное',[(4,'План на отм. 0,000, Разрез 1-1')]),
 ('КДС-2026-1-27.01-АР (1).pdf','Гараж',[(4,'План на отм. 0,000, Разрез 1-1')])]
out=fitz.open(); toc=[]
for f,name,pp in sel:
    s=fitz.open(D+f)
    toc.append([1,name,out.page_count+1])
    for p,t in pp:
        out.insert_pdf(s,from_page=p-1,to_page=p-1)
        toc.append([2,t,out.page_count])
        if sys.argv[1:]: out[-1].get_pixmap(dpi=40).save(f'th_{out.page_count:02d}.png')
out.set_toc(toc)
dst=D+'КДС-2026-1_АР_Планы 1 этажа и разрезы.pdf'
out.save(dst,garbage=3,deflate=True); print(dst,out.page_count)
