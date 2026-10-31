# Dynamo Implementation Map — Oncology-ready

Мақсат: Oncology профиліндегі принциптерді Revit/Dynamo-да қайталанатын алгоритмге айналдыру.

## A. Input layer

1. Revit: Levels, Grids, Structural Foundations, Columns, Walls, Framing, Floors, Openings, Stairs.
2. Calculation input: As_req by coordinate / element / face / direction.
3. Project profile: [[12_Oncology_Project_Profile]].
4. User rules: Current Rules from [[00_KJ_Dynamo_Hub]].
5. Source tables/import: mark, position, Ø, class, length/metrage, quantity, source mass, sheet.

Барлық input бір `RunID + ProjectID + RevisionID` арқылы бекітіледі.

## B. Element registry

Әр Revit элементке:
- ElementUID;
- Category;
- ElementMark;
- Level/LevelRange;
- GridLocation;
- GeometryHash;
- ProjectProfile;
- SourceSheet;
- ConflictStatus.

Марка мен экземплярды бөлек сақтау: бір марка бірнеше Revit instance-ке тарайды.

## C. Reinforcement record

Негізгі record:
`RebarKey = Project|Revision|Category|Mark|Assembly|Position|LevelZone|Face|Direction`.

Fields: Ø, SteelClass, ShapeCode, LengthEach, TotalRunningLength, Qty, Spacing, ZoneLength, Face, Direction, Role, HostUID, CoverReference, LapType, LapLength, LapIncluded, Anchorage, AssemblyParent, AssemblyFactor, SourceMass, CalcMass, WasteIncluded, SourceSheet, Status.
## D. Graph modules

### G00_Project_Init
Project/Revision, units, rule version, profile, logging.

### G01_Geometry_Registry
Ось/деңгей/host геометриясын оқиды, марка–экземпляр реестрін жасайды.

### G02_As_Mapper
As_req координаттарын host face/direction/zone-ға байланыстырады.

### G03_Foundation
Bottom/Top × X/Y бөлек; main/additional zones; edges/openings; Кр/фиксатор; releases.

### G04_Columns
Section changes by level; longitudinal groups; tie zones; node meshes; lap/overlay transitions.

### G05_Walls
Face A/B × Vertical/Horizontal; field/boundary/opening/intersection zones; pins and edge cages.

### G06_Rigels
Multi-span station model; top/bottom longitudinal groups; support/span additions; transverse zones.

### G07_Slabs
Level-specific Bottom/Top × X/Y; openings; edge anchorage; support details; local cover Pm-6.

### G08_Stairs_Parapets
Separate categories, type quantities, welded meshes and project-specific supports.

### G09_Assemblies
Nested С1/С2/Кр1/mesh assemblies; parent-child relation; no double-counting.

### G10_Splices_Anchorage
Rule resolver: current-user-rule → project-profile → unresolved exception.

### G11_Rebar_Create_Update
Idempotent creation: update by RebarKey; preserve ManualOverride.

### G12_Schedules_Drawings
Marks, positions, details, views, schedules, mass, source references.

### G13_QA
Run all checks from [[11_QA_Checks]], create Exception Register.
## E. Rule resolver priority

1. Manual Override / latest explicit Bekassyl decision.
2. Current Rules.
3. Project Profile confirmed/accepted field.
4. Source drawing value if no conflict.
5. If conflict or missing structural decision → do not guess; Status=Unresolved and send to QA report.

No source-only number may silently become a global rule.

## F. Idempotency

Repeated Run must not create duplicate Rebar.
Search existing elements by RebarKey + HostUID.
If geometry/rules changed, update or replace only controlled generated objects.
ManualOverride=true objects are never overwritten; they are compared and reported.

## G. Output sets

- Revit Rebar / assemblies.
- Mark and position register.
- Reinforcement schedule.
- Mass by element/mark/level/project.
- Assembly hierarchy report.
- Conflict / unresolved register.
- QA report with ElementUID, rule, expected, actual, action.
- Source trace: PDF sheet / accepted user decision / rule version.

## H. Oncology test dataset

Regression tests must include at minimum:
- Фм-1 поз.11 source43 vs accepted55;
- Км-8.1 Ø20 source vs acceptedØ28;
- См-9 thickness250/200 unresolved;
- Рм-30 quantity unresolved;
- Парапет Шп1 A500C/A240 unresolved;
- Кр1 nested mass no double count;
- running-metre row with LapIncluded=true;
- Pm-6 local cover distinct from Pm-1…Pm-5.
