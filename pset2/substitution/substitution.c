#include <stdio.h>
#include <cs50.h>
#include <ctype.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, string argv[])
{
    //check there's only one command line argument and it's 26 characters long
    if ((argc != 2) || (strlen(argv[1]) != 26))
    {
        printf("Usage: ./substitution key\n");
        return 1;
    }
    //check the command line argument is all letters
    for (int i = 0; i < strlen(argv[1]); i += 1)
    {
        if (isalpha(argv[1][i]) == false)
        {
            printf("Usage: ./substitution key\n");
            return 1;
        }
    }
    //check the command line argument has each letter occuring only once
    for (int i = 0; i < strlen(argv[1]); i += 1)
    {
        for (int j = i; j < strlen(argv[1]); j += 1)
        {
            if (argv[1][i] == argv[1][j])
            {
            printf("Characters in key are not unique\n");
            return 1;
            }
        }
    }
    //declare variables
    string keyupper;
    string keylower;
    string key;
    key = argv[1];
    keyupper = toupper(key);
    keylower = tolower(key);
    //get plaintext from user
    string plaintext = get_string("plaintext: ");

    //for each letter in plaintext, print the correctvalue from the appropriate key
    printf("ciphertext: ");
    for (int i = 0; i < strlen(plaintext); i += 1)
    {
        //if uppercase, rotate
        if (isupper(plaintext[i]))
        {
            printf("%c", (keyupper[plaintext[i] - 65]);
        }
        //if lowercase, rotate
        else if (islower(plaintext[i]))
        {
            printf("%c", (keylower[plaintext[i] - 97]);
        }
        //if other, leave as is
        else
        {
            printf("%c", plaintext[i]);
        }
    }
    //new line and return 0
    printf("\n");
    return 0;
}