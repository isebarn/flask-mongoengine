from os import system

file = open("schema.txt", "r")
Lines = file.readlines()

count = 0
# Strips the newline character

template = open("./_models.txt", "r")
class_string = template.readlines()
restx_model = []

# models go in singular and come out plural
# sellers: seller
path_dict = {"image": "images", "product": "products", "user": "users"}


in_class = False
classes = []
inherit = None
for line in [x.strip() for x in Lines]:
    if line.startswith("// inherits"):
        inherit = line.split()[-1]
    elif line.startswith("table") and line.endswith("{"):
        classname = line.split()[1]
        class_string.append(
            "class {}({}):\n".format(
                "".join([x.capitalize() for x in classname.split("_")]),
                inherit or "Extended",
            )
        )

        restx_model.append(
            "{} = api.clone('{}', base, {{\n".format(classname, classname.capitalize())
        )

        in_class = True
        inherit = None
        classes.append(classname)

    elif in_class:

        if line.startswith("id "):
            continue

        elif line.startswith("}"):
            in_class = False
            class_string.append("\n\n")
            restx_model.append("})\n\n")

        else:
            class_string.append("    {} = ".format(line.split()[0]))

            if "[ref:" in line:
                ref_field = line.split("> ")[-1].split(".")[0]
                class_string.append(
                    "ReferenceField({})\n".format(ref_field.capitalize())
                )
                restx_model.append(
                    "    '{}': Nested({}),\n".format(line.split()[0], ref_field)
                )
            elif line.split()[1] == "varchar":
                class_string.append("StringField()\n")
                restx_model.append("    '{}': String,\n".format(line.split()[0]))
            elif line.split()[1] == "datetime":
                class_string.append("DateTimeField()\n")
                restx_model.append(
                    "    '{}': DateTime(attribute=lambda x: datetime.fromtimestamp(x.get('{}', {{}}).get('$date', 0)/1e3)),\n".format(
                        line.split()[0], line.split()[0]
                    )
                )
            elif line.split()[1] == "float":
                class_string.append("FloatField()\n")
                restx_model.append("    '{}': Float,\n".format(line.split()[0]))
            elif line.split()[1] == "boolean":
                class_string.append("BooleanField(default=False)\n")
                restx_model.append("    '{}': Boolean,\n".format(line.split()[0]))
            elif line.split()[1] == "dict":
                class_string.append("DictField()\n")
                restx_model.append("    '{}': Raw(),\n".format(line.split()[0]))


file = open("../models/__init__.py", "w")
file.writelines(class_string)

template = open("./_models_end.txt", "r")
class_string = template.readlines()
file.writelines(class_string)

file.close()


api_document = open("./_endpoints.txt", "r")
api_document = api_document.readlines()

file = open("../endpoints/__init__.py", "w")
file.writelines(api_document)
file.writelines(restx_model)
file.writelines("\n\n")

for item in classes:
    controller_template = open("./_endpoint.txt", "r")
    controller_template = controller_template.readlines()
    controller_template = "".join(controller_template)
    controller_template = controller_template.replace(
        "CONTROLLER", "".join([x.capitalize() for x in path_dict[item].split("_")])
    )
    controller_template = controller_template.replace("controller", path_dict[item])
    controller_template = controller_template.replace("RESTX_MODEL", item)
    controller_template = controller_template.replace(
        "MODEL", "".join([x.capitalize() for x in item.split("_")])
    )

    file.writelines(controller_template)

# file.writelines(["    return api\n\n"])
file.close()

main_file = open("./main.txt", "r")
main = open("../main.py", "w")
main.writelines(main_file)
main_file.close()
main.close()

system("python3 -m black ../")
