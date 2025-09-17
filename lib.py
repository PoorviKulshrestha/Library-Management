from libraryclass import library

def main():
    Lib = library()
    print("     ===== WELCOME TO LIBRARY MANAGEMENT SYSTEM =====\n")
    while True:
        print(
            "Please Enter your choice :\n"
            "1.Display available books\n"
            "2.View and Borrow a book\n"
            "3.Return a book\n"
            "4.Sort books in ascending/descending order\n"
            "5.Display current views of each book\n"
            "6.Donate a book\n"
            "7.Exit"
        )

        try:
            choice = int(input("Enter your choice number: "))
        except ValueError:
            print("\nInvalid input. Please enter a number.\n")
            continue

        if choice == 1:
            Lib.display()

        elif choice == 2:
            Lib.view_book()

        elif choice == 3:
            # Return now requires a 4-digit Book-ID
            book_id = input("\nEnter the 4-digit Book-ID you want to return: ").strip()
            Lib.return_book(book_id)

        elif choice == 4:
            Lib.sort_books()

        elif choice == 5:
            Lib.count_views()

        elif choice == 6:          # <-- new option
            Lib.donate_book()

        elif choice == 7:
            print("\nThank you for using library management system.")
            break

        else:
            print("\nInvalid choice. Please enter a valid number.\n")


if __name__ == "__main__":
    main()
