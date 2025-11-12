using Microsoft.Extensions.Configuration;
using System.IO;

public static class ConfigurationManager
{
    private static IConfigurationRoot _configuration;

    static ConfigurationManager()
    {
        _configuration = new ConfigurationBuilder()
            .SetBasePath(Directory.GetCurrentDirectory())
            .AddJsonFile("appsettings.json", optional: false, reloadOnChange: true);
            .Build();
    }

    public static string BaseUrl
    {
        get
        {
            return _configuration["Settings:BaseUrl"];
        }
    }

    public static TimeSpan DefaultWaitTime
    {
        get
        {
            int seconds = int.Parse(_configuration["Settings:DefaultWaitSeconds"]);
            return TimeSpan.FromSeconds(seconds);
        }
    }
}