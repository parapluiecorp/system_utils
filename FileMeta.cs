using System;
using System.IO;
using System.Security.Cryptography;

class FileMeta
{
    static int Main(string[] args)
    {
        Console.Write("Enter full file path: ");
        string path = Console.ReadLine()?.Trim();

        if (string.IsNullOrWhiteSpace(path))
        {
            Console.Error.WriteLine("Error: No path provided.");
            return 1;
        }

        try
        {
            if (!File.Exists(path))
            {
                Console.Error.WriteLine("Error: File not found.");
                return 1;
            }

            FileInfo info = new FileInfo(path);

            Console.WriteLine("\n=== FILE METADATA ===");
            Console.WriteLine($"Full Name:         {info.FullName}");
            Console.WriteLine($"Name:              {info.Name}");
            Console.WriteLine($"Extension:         {info.Extension}");
            Console.WriteLine($"Size (bytes):      {info.Length}");
            Console.WriteLine($"Created:           {info.CreationTime}");
            Console.WriteLine($"Last Modified:     {info.LastWriteTime}");
            Console.WriteLine($"Last Accessed:     {info.LastAccessTime}");
            Console.WriteLine($"Attributes:        {info.Attributes}");

            // Optional hash
            /*
            try
            {
                using var stream = info.OpenRead();
                using var sha1 = SHA1.Create();
                byte[] hash = sha1.ComputeHash(stream);
                Console.WriteLine("SHA1 Hash:         " +
                    BitConverter.ToString(hash).Replace("-", ""));
            }
            catch (UnauthorizedAccessException)
            {
                Console.WriteLine("SHA1 Hash:         (access denied)");
            }
            */

            return 0;
        }
        catch (UnauthorizedAccessException)
        {
            Console.Error.WriteLine("Error: Access denied.");
            return 1;
        }
        catch (IOException ex)
        {
            Console.Error.WriteLine($"I/O Error: {ex.Message}");
            return 1;
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine($"Unexpected error: {ex.Message}");
            return 1;
        }
    }
}

