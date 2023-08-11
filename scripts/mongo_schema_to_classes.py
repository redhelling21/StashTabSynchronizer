import json

classesToCreate = {}


# Function to generate C# classes from the MongoDB schema
def generate_csharp_classes(schema):
    finalCode = "using System;\nusing System.Collections.Generic;\n\n"
    fields = schema["Fields"]
    classesToCreate["root"] = {"name": "root", "properties": list()}
    for field in fields:
        structure = field["fullPath"].split(".")
        if len(structure) == 1:
            classesToCreate["root"]["properties"].append(create_property(field))
        else:
            recreate_structure(structure.pop())
    for key in classesToCreate:
        finalCode += print_class(classesToCreate[key])
    return finalCode


def capitalize_first_letter(text):
    return text[0].upper() + text[1:]


def print_class(classToCreate):
    if classToCreate["name"].isnumeric():
        return ""
    classCode = f"public class {capitalize_first_letter(classToCreate['name'])}\n" + "{\n"
    for prop in classToCreate["properties"]:
        if prop is not None and not prop["name"].isnumeric():
            propCode = f"\tpublic {prop['type']}{'?' if prop['nullable'] else ''} {capitalize_first_letter(prop['name'])}" + "{ get; set; }\n"
            classCode += propCode
    classCode += "}\n\n"
    return classCode


def recreate_structure(structure):
    for layer in structure:
        if layer not in classesToCreate:
            classesToCreate[layer] = {"name": layer, "properties": list()}


def create_property(field):
    prop = {}
    prop["name"] = field["field"]
    prop["nullable"] = field["probability"] < 1
    typename = get_type_mapping_for(field["types"][0]["typename"])

    if typename == "object":
        if prop["name"] not in classesToCreate:
            classesToCreate[prop["name"]] = {"name": prop["name"], "properties": list()}
        for subItem in field.get("subItems", []):
            classesToCreate[prop["name"]]["properties"].append(create_property(subItem))
        typename = capitalize_first_letter(prop["name"])

    elif typename == "List":
        if "subItems" in field:
            if prop["name"] not in classesToCreate:
                classesToCreate[prop["name"]] = {"name": f"{prop['name']}Content", "properties": list()}
            for subItem in field.get("subItems", []):
                classesToCreate[prop["name"]]["properties"].append(create_property(subItem))
            typename = f"List<{capitalize_first_letter(prop['name'])}Content>"
        else:
            typename = "List<string>"
    elif typename == "Null":
        return None
    prop["type"] = typename
    return prop


def get_type_mapping_for(typename):
    mapping = {
        "ObjectId": "string",
        "String": "string",
        "Int32": "int",
        "Array": "List",
        "Object": "object",  # You can update this for your specific "Object" classes
        "Bool": "bool",
        "Array(Empty)": "Null",
    }
    return mapping.get(typename, "object")


if __name__ == "__main__":
    with open("scripts/schema.json", "r") as file:
        schema_json = json.load(file)

    csharp_classes = generate_csharp_classes(schema_json)
    with open("scripts/generated_classes.cs", "w") as file:
        file.write(csharp_classes)
