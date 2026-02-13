import { useAuth } from "@/_core/hooks/useAuth";
import DashboardLayout from "@/components/DashboardLayout";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Upload, Calendar, BarChart3, Settings } from "lucide-react";
import { trpc } from "@/lib/trpc";

export default function Dashboard() {
  const { user } = useAuth();
  const { data: artPieces } = trpc.artPieces.list.useQuery();
  const { data: scheduledPosts } = trpc.scheduledPosts.list.useQuery();
  const { data: postHistory } = trpc.postHistory.list.useQuery();

  if (!user) {
    return <div>Loading...</div>;
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Art Curator & Automator</h1>
          <p className="text-muted-foreground mt-2">
            Manage, curate, and automate your art posts across social media platforms
          </p>
        </div>

        <Tabs defaultValue="overview" className="space-y-4">
          <TabsList>
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="upload">Upload Art</TabsTrigger>
            <TabsTrigger value="schedule">Schedule Posts</TabsTrigger>
            <TabsTrigger value="history">Post History</TabsTrigger>
            <TabsTrigger value="settings">Settings</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium">Total Art Pieces</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{artPieces?.length || 0}</div>
                  <p className="text-xs text-muted-foreground">Uploaded and processed</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium">Scheduled Posts</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {scheduledPosts?.filter((p) => p.status === "scheduled").length || 0}
                  </div>
                  <p className="text-xs text-muted-foreground">Waiting to publish</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium">Published Posts</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{postHistory?.length || 0}</div>
                  <p className="text-xs text-muted-foreground">Across all platforms</p>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="upload" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Upload Art Piece</CardTitle>
                <CardDescription>
                  Upload your generated art for processing and curation
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="border-2 border-dashed border-border rounded-lg p-12 text-center">
                  <Upload className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                  <p className="text-sm font-medium mb-2">Drag and drop your art here</p>
                  <p className="text-xs text-muted-foreground mb-4">
                    or click to browse (PNG, JPEG, WebP)
                  </p>
                  <Button variant="outline">Select File</Button>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Title</label>
                  <input
                    type="text"
                    placeholder="Enter art piece title"
                    className="w-full px-3 py-2 border border-border rounded-md"
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Description</label>
                  <textarea
                    placeholder="Describe your artwork"
                    className="w-full px-3 py-2 border border-border rounded-md"
                    rows={4}
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Tags</label>
                  <input
                    type="text"
                    placeholder="art, digital, abstract (comma-separated)"
                    className="w-full px-3 py-2 border border-border rounded-md"
                  />
                </div>

                <Button className="w-full">Upload & Process</Button>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="schedule" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Schedule Post</CardTitle>
                <CardDescription>
                  Create and schedule posts to publish across platforms
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Select Art Piece</label>
                  <select className="w-full px-3 py-2 border border-border rounded-md">
                    <option>Choose an art piece...</option>
                    {artPieces?.map((piece) => (
                      <option key={piece.id} value={piece.id}>
                        {piece.title}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Caption</label>
                  <textarea
                    placeholder="Write your post caption"
                    className="w-full px-3 py-2 border border-border rounded-md"
                    rows={3}
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Hashtags</label>
                  <input
                    type="text"
                    placeholder="#art #digital #artist"
                    className="w-full px-3 py-2 border border-border rounded-md"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Schedule Date</label>
                    <input type="date" className="w-full px-3 py-2 border border-border rounded-md" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Schedule Time</label>
                    <input type="time" className="w-full px-3 py-2 border border-border rounded-md" />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Platforms</label>
                  <div className="space-y-2">
                    <label className="flex items-center">
                      <input type="checkbox" className="mr-2" defaultChecked />
                      <span className="text-sm">X (Twitter)</span>
                    </label>
                    <label className="flex items-center">
                      <input type="checkbox" className="mr-2" />
                      <span className="text-sm">Instagram</span>
                    </label>
                    <label className="flex items-center">
                      <input type="checkbox" className="mr-2" />
                      <span className="text-sm">Facebook</span>
                    </label>
                  </div>
                </div>

                <Button className="w-full">Schedule Post</Button>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="history" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Post History</CardTitle>
                <CardDescription>View all published posts and engagement metrics</CardDescription>
              </CardHeader>
              <CardContent>
                {postHistory && postHistory.length > 0 ? (
                  <div className="space-y-4">
                    {postHistory.map((post) => (
                      <div
                        key={post.id}
                        className="border border-border rounded-lg p-4 space-y-2"
                      >
                        <div className="flex justify-between items-start">
                          <div>
                            <p className="font-medium capitalize">{post.platform}</p>
                            <p className="text-sm text-muted-foreground">{post.caption}</p>
                          </div>
                          <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                            {post.status}
                          </span>
                        </div>
                        <p className="text-xs text-muted-foreground">
                          Published: {new Date(post.publishedAt).toLocaleString()}
                        </p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground text-center py-8">
                    No posts published yet
                  </p>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="settings" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Social Media Accounts</CardTitle>
                <CardDescription>Connect your social media accounts</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <p className="text-sm font-medium">Connected Accounts</p>
                  <div className="space-y-2">
                    <div className="border border-border rounded-lg p-3 flex justify-between items-center">
                      <span className="text-sm">X (Twitter)</span>
                      <Button variant="outline" size="sm">
                        Manage
                      </Button>
                    </div>
                    <div className="border border-border rounded-lg p-3 flex justify-between items-center">
                      <span className="text-sm">Instagram</span>
                      <Button variant="outline" size="sm">
                        Connect
                      </Button>
                    </div>
                    <div className="border border-border rounded-lg p-3 flex justify-between items-center">
                      <span className="text-sm">Facebook</span>
                      <Button variant="outline" size="sm">
                        Connect
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  );
}
