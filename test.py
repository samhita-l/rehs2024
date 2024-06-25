def main():
    value = "module=intel-mpi/2019.10.317/ezrfjne"
    text = value.split("=")
    temp = text[1]
    name = temp.split("/")
    print(name[1])

if __name__ == "__main__":
    main()
