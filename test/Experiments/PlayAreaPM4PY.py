import pm4py
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.petri_net.importer import importer as pnml_importer

net, initial_marking, final_marking = pnml_importer.apply("8.pnml")

log = pm4py.read_xes("Repair_alpha_logwise_oneRperPoVar.xes")
df = log_converter.apply(log, variant=log_converter.Variants.TO_DATA_FRAME)
intM = 3
indentiy_id = log["identity:id"]
intB = 4
column_names = df.columns
print(column_names)
print(df.head(1))