using Newtonsoft.Json;

namespace VideoStreamingTests.Models
{
    public class Comment
    {
        [JsonProperty("id")] public int Id { get; set; }
        [JsonProperty("video_id")] public int VideoId { get; set; }
        [JsonProperty("author")] public string Author { get; set; }
        [JsonProperty("text")] public string Text { get; set; }
        [JsonProperty("created_at")] public DateTime CreatedAT { get; set; }
        [JsonProperty("likes_count")] public int LikesCount { get; set; }
        [JsonProperty("dislikes_count")] public int DislikesCount { get; set; }
    }
}