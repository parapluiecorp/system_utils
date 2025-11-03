using System;
using System.IO;

class FileMeta
{
    static void Main(string[] args)
    {
        Console.Write("Enter full file path: ");
        string path = Console.ReadLine();

        if (String.IsNullOrWhiteSpace(path))
        {
            Console.WriteLine("No path provided.");
            return;
        }

        if (!File.Exists(path))
        {
            Console.WriteLine("File not found.");
            return;
        }

        FileInfo info = new FileInfo(path);

        Console.WriteLine("\n=== FILE METADATA ===");
        Console.WriteLine("Full Name:         " + info.FullName);
        Console.WriteLine("Name:              " + info.Name);
        Console.WriteLine("Extension:         " + info.Extension);
        Console.WriteLine("Size (bytes):      " + info.Length);
        Console.WriteLine("Created:           " + info.CreationTime);
        Console.WriteLine("Last Modified:     " + info.LastWriteTime);
        Console.WriteLine("Last Accessed:     " + info.LastAccessTime);
        Console.WriteLine("Attributes:        " + info.Attributes);

        // Optional: Hash
        /*
        try
        {
            using (var stream = info.OpenRead())
            {
                var sha1 = System.Security.Cryptography.SHA1.Create();
                var hash = sha1.ComputeHash(stream);
                Console.WriteLine("SHA1 Hash:         " +
                    BitConverter.ToString(hash).Replace("-", ""));
            }
        }
        catch
        {
            Console.WriteLine("SHA1 Hash:         (access denied)");
        }
        */
    }
}

