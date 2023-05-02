import json
import discord
import voicelink
from collections import deque
import random
import numpy as np
import networkx as nx

from function import (
    get_lang,
    get_aliases,
    cooldown_check
)
from discord import app_commands
from discord.ext import commands


async def check_access(ctx: commands.Context):
    player: voicelink.Player = ctx.guild.voice_client
    if not player:
        raise voicelink.VoicelinkException(get_lang(ctx.guild.id, 'noPlayer'))

    if ctx.author not in player.channel.members:
        if not ctx.author.guild_permissions.manage_guild:
            return await ctx.send(player.get_msg('notInChannel').format(ctx.author.mention, player.channel.mention), ephemeral=True)

    return player


class Effect(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.description = "This category is only available to DJ on this server. (You can setdj on your server by /settings setdj <DJ ROLE>)"
    async def effect_autocomplete(self, interaction: discord.Interaction, current: str) -> list:
        player: voicelink.Player = interaction.guild.voice_client
        if not player:
            return []
        if current:
            return [app_commands.Choice(name=effect.tag, value=effect.tag) for effect in player.filters.get_filters() if current in effect.tag]
        return [app_commands.Choice(name=effect.tag, value=effect.tag) for effect in player.filters.get_filters()]

    @commands.hybrid_command(name="speed", aliases=get_aliases("speed"))
    @app_commands.describe(value="The value to set the speed to. Default is `1.0`")
    @commands.dynamic_cooldown(cooldown_check, commands.BucketType.guild)
    async def speed(self, ctx: commands.Context, value: commands.Range[float, 0, 2]):
        "Sets the player's playback speed"
        player = await check_access(ctx)

        if player.filters.has_filter(filter_tag="speed"):
            player.filters.remove_filter(filter_tag="speed")
        await player.add_filter(voicelink.Timescale(tag="speed", speed=value))
        await ctx.send(f"You set the speed to **{value}**.")

    @commands.hybrid_command(name="karaoke", aliases=get_aliases("karaoke"))
    @app_commands.describe(
        level="The level of the karaoke. Default is `1.0`",
        monolevel="The monolevel of the karaoke. Default is `1.0`",
        filterband="The filter band of the karaoke. Default is `220.0`",
        filterwidth="The filter band of the karaoke. Default is `100.0`"
    )
    @commands.dynamic_cooldown(cooldown_check, commands.BucketType.guild)
    async def karaoke(self, ctx: commands.Context, level: commands.Range[float, 0, 2] = 1.0, monolevel: commands.Range[float, 0, 2] = 1.0, filterband: commands.Range[float, 100, 300] = 220.0, filterwidth: commands.Range[float, 50, 150] = 100.0) -> None:
        "Uses equalization to eliminate part of a band, usually targeting vocals."
        player = await check_access(ctx)

        if player.filters.has_filter(filter_tag="karaoke"):
            player.filters.remove_filter(filter_tag="karaoke")
        await player.add_filter(voicelink.Karaoke(tag="karaoke", level=level, mono_level=monolevel, filter_band=filterband, filter_width=filterwidth))
        await ctx.send(player.get_msg('karaoke').format(level, monolevel, filterband, filterwidth))

    @commands.hybrid_command(name="bfs", aliases=get_aliases("bfs"))
    @commands.dynamic_cooldown(cooldown_check, commands.BucketType.guild)
    async def bfs(self, ctx: commands.Context):
        await ctx.send("""BFS viết tắt của Breadth-First Search, là một thuật toán tìm kiếm theo chiều rộng. Nó khởi đầu từ một đỉnh gốc và khám phá tất cả các đỉnh kề cận trước khi di chuyển đến các đỉnh xa hơn. BFS sử dụng hàng đợi để theo dõi các đỉnh đã khám phá và các đỉnh chưa khám phá đến. Nó khởi tạo bằng cách thêm đỉnh gốc vào hàng đợi. Sau đó nó lấy đỉnh đầu tiên ra khỏi hàng đợi, khám phá tất cả đỉnh kề cận của nó và thêm chúng vào hàng đợi.Quá trình này được lặp lại cho đến khi hàng đợi trống.
triển khai BFS tiêu chuẩn sẽ đặt mỗi đỉnh của đồ thị vào một trong hai loại: visited, not visited. Mục đích của thuật toán là đánh dấu mỗi đỉnh là đã thăm để tránh các chu trình.

Cách thuật toán hoạt động như sau:

1.Lấy một đỉnh bất kỳ trong đồ thị thêm vào cuối hàng đợi.
2.Lấy phân tử đầu tiên của hàng đợi và thêm nó vào danh sách đã duyệt.
3.Tạo một danh sách các đỉnh liền kề của đỉnh đang xét. Thêm những đỉnh không có trong danh sách đã duyệt vào cuối hàng đợi.
4.Tiếp tục lặp lại bước 2 và 3 cho đến khi hàng đợi trống.
Lưu ý: Đồ thị có thể chứa hai thành phần không liên kết khác nhau, vì vậy để đảm bảo rằng mọi đỉnh đều đã được thăm, chúng ta cũng có thể chạy thuật toán BFS trên mọi đỉnh.
                """)

    @commands.hybrid_command(name="hill_climbing", aliases=get_aliases("hill_climbing"))
    @commands.dynamic_cooldown(cooldown_check, commands.BucketType.guild)
    async def hill_climbing(self, ctx: commands.Context):
        await ctx.send("""Hill Climbing Algorithm là một thuật toán tìm kiếm cục bộ liên tục di chuyển theo hướng tăng dần giá trị để tìm ra đỉnh hoặc giải pháp tốt nhất cho vấn đề. Nó kết thúc khi nó đạt đến giá trị cao nhất mà không có giải pháp nào có giá trị cao hơn.

Hill Climbing Algorithm là một kỹ thuật được sử dụng để tối ưu hóa các vấn đề toán học. Một trong những ví dụ được thảo luận rộng rãi về Hill Climbing Algorithm là Bài toán nhân viên bán hàng đi lại, trong đó chúng ta cần giảm thiểu khoảng cách di chuyển của nhân viên bán hàng.

Mô tả thuật toán

B1: Xét trạng thái đầu: Nếu là đích => dừng

Ngược lại, thiết lập trạng thái bắt đầu = trạng thái hiện tại.

B2: Lựa một luật để áp dụng vào trạng thái hiện tại để sinh ra một trạng thái mới.

B3: Xem xét trạng thái mới này:

Nếu là đích => dừng.

Nếu không phải là đích nhưng tốt hơn trạng thái hiện tại thì thiết lập trạng thái hiệu t là trạng thái mới.

Nếu không tốt hơn thì đến trạng thái mới tiếp theo

Lặp đến khi: gặp đích hoặt không còn luật nào nữa chưa được áp dụng vào trạng thái hiện tại.
        """)


    @commands.hybrid_command(name="bfssearch", aliases=get_aliases("bfssearch"))
    @commands.dynamic_cooldown(cooldown_check, commands.BucketType.guild)
    async def bfssearch(self, ctx: commands.Context, start: str, target: str, *, graph: str):
        graph = json.loads(graph)

        def bfs(start, end, graph):
            visited = set()
            queue = deque([(start, [start])])
        
            while queue:
                (node, path) = queue.popleft()
                if node == end:
                    return path
                if node not in visited:
                    visited.add(node)
                    neighbors = graph[node]
                    for neighbor in neighbors:
                        if neighbor not in visited:
                            queue.append((neighbor, path + [neighbor]))

        path = bfs(start, target, graph)
        await ctx.send(f"Shortest path from {start} to {target}: {path}")


    @commands.hybrid_command(name="hillsearch", aliases=get_aliases("hillsearch"))
    @commands.dynamic_cooldown(cooldown_check, commands.BucketType.guild)
    async def hillsearch(self, ctx: commands.Context, *, array: str):
        coordinate = np.array(json.loads(array))
        def generate_matrix(coordinate):
            matrix = []
            for i in range(len(coordinate)):
                for j in range(len(coordinate)) :       
                    p = np.linalg.norm(coordinate[i] - coordinate[j])
                    matrix.append(p)
            matrix = np.reshape(matrix, (len(coordinate),len(coordinate)))
            #print(matrix)
            return matrix
        
        #finds a random solution    
        def solution(matrix):
            points = list(range(0, len(matrix)))
            solution = []
            for i in range(0, len(matrix)):
                random_point = points[random.randint(0, len(points) - 1)]
                solution.append(random_point)
                points.remove(random_point)

            return solution
        #computes the path based on the random solution
        def path_length(matrix, solution):
            cycle_length = 0
            for i in range(0, len(solution)):
                cycle_length += matrix[solution[i]][solution[i - 1]]
            return cycle_length

        #generate neighbors of the random solution by swapping cities and returns the best neighbor
        def neighbors(matrix, solution):
            neighbors = []
            for i in range(len(solution)):
                for j in range(i + 1, len(solution)):
                    neighbor = solution.copy()
                    neighbor[i] = solution[j]
                    neighbor[j] = solution[i]
                    neighbors.append(neighbor)
            
            #assume that the first neighbor in the list is the best neighbor      
            best_neighbor = neighbors[0]
            best_path = path_length(matrix, best_neighbor)
    
            #check if there is a better neighbor
            for neighbor in neighbors:
                current_path = path_length(matrix, neighbor)
                if current_path < best_path:
                    best_path = current_path
                    best_neighbor = neighbor
            return best_neighbor, best_path
    
        def hill_climbing(coordinate):
            matrix = generate_matrix(coordinate)
    
            current_solution = solution(matrix)
            current_path = path_length(matrix, current_solution)
            neighbor = neighbors(matrix,current_solution)[0]
            best_neighbor, best_neighbor_path = neighbors(matrix, neighbor)

            while best_neighbor_path < current_path:
                current_solution = best_neighbor
                current_path = best_neighbor_path
                neighbor = neighbors(matrix, current_solution)[0]
                best_neighbor, best_neighbor_path = neighbors(matrix, neighbor)

            return current_path, current_solution

        final_solution = hill_climbing(coordinate)
        await ctx.send(f"The solution is \n {final_solution[1]}, \nThe path length is \n {final_solution[0]}")
       
        
        


    @commands.hybrid_command(name="tremolo", aliases=get_aliases("tremolo"))
    @app_commands.describe(
        frequency="The frequency of the tremolo. Default is `2.0`",
        depth="The depth of the tremolo. Default is `0.5`"
    )
    @commands.dynamic_cooldown(cooldown_check, commands.BucketType.guild)
    async def tremolo(self, ctx: commands.Context, frequency: commands.Range[float, 0, 10] = 2.0, depth: commands.Range[float, 0, 1] = 0.5) -> None:
        "Uses amplification to create a shuddering effect, where the volume quickly oscillates."
        player = await check_access(ctx)

        if player.filters.has_filter(filter_tag="tremolo"):
            player.filters.remove_filter(filter_tag="tremolo")
        await player.add_filter(voicelink.Tremolo(tag="tremolo", frequency=frequency, depth=depth))
        await ctx.send(player.get_msg('tremolo&vibrato').format(frequency, depth))

    @commands.hybrid_command(name="vibrato", aliases=get_aliases("vibrato"))
    @app_commands.describe(
        frequency="The frequency of the vibrato. Default is `2.0`",
        depth="The Depth of the vibrato. Default is `0.5`"
    )
    @commands.dynamic_cooldown(cooldown_check, commands.BucketType.guild)
    async def vibrato(self, ctx: commands.Context, frequency: commands.Range[float, 0, 14] = 2.0, depth: commands.Range[float, 0, 1] = 0.5) -> None:
        "Similar to tremolo. While tremolo oscillates the volume, vibrato oscillates the pitch."
        player = await check_access(ctx)

        if player.filters.has_filter(filter_tag="vibrato"):
            player.filters.remove_filter(filter_tag="vibrato")
        await player.add_filter(voicelink.Vibrato(tag="vibrato", frequency=frequency, depth=depth))
        await ctx.send(player.get_msg('tremolo&vibrato').format(frequency, depth))

    @commands.hybrid_command(name="rotation", aliases=get_aliases("rotation"))
    @app_commands.describe(hertz="The hertz of the rotation. Default is `0.2`")
    @commands.dynamic_cooldown(cooldown_check, commands.BucketType.guild)
    async def rotation(self, ctx: commands.Context, hertz: commands.Range[float, 0, 2] = 0.2) -> None:
        "Rotates the sound around the stereo channels/user headphones aka Audio Panning."
        player = await check_access(ctx)

        if player.filters.has_filter(filter_tag="rotation"):
            player.filters.remove_filter(filter_tag="rotation")
        await player.add_filter(voicelink.Rotation(tag="rotation", rotation_hertz=hertz))
        await ctx.send(player.get_msg('rotation').format(hertz))

    @commands.hybrid_command(name="distortion", aliases=get_aliases("distortion"))
    @commands.dynamic_cooldown(cooldown_check, commands.BucketType.guild)
    async def distortion(self, ctx: commands.Context) -> None:
        "Distortion effect. It can generate some pretty unique audio effects."
        player = await check_access(ctx)

        if player.filters.has_filter(filter_tag="distortion"):
            player.filters.remove_filter(filter_tag="distortion")
        await player.add_filter(voicelink.Distortion(tag="distortion", sin_offset=0.0, sin_scale=1.0, cos_offset=0.0, cos_scale=1.0, tan_offset=0.0, tan_scale=1.0, offset=0.0, scale=1.0))
        await ctx.send(player.get_msg('distortion'))

    @commands.hybrid_command(name="lowpass", aliases=get_aliases("lowpass"))
    @app_commands.describe(smoothing="The level of the lowPass. Default is `20.0`")
    @commands.dynamic_cooldown(cooldown_check, commands.BucketType.guild)
    async def lowpass(self, ctx: commands.Context, smoothing: commands.Range[float, 10, 30] = 20.0) -> None:
        "Filter which supresses higher frequencies and allows lower frequencies to pass."
        player = await check_access(ctx)

        if player.filters.has_filter(filter_tag="lowpass"):
            player.filters.remove_filter(filter_tag="lowpass")
        await player.add_filter(voicelink.LowPass(tag="lowpass", smoothing=smoothing))
        await ctx.send(player.get_msg('lowpass').format(smoothing))

    @commands.hybrid_command(name="channelmix", aliases=get_aliases("channelmix"))
    @app_commands.describe(
        left_to_left="Sounds from left to left. Default is `1.0`",
        right_to_right="Sounds from right to right. Default is `1.0`",
        left_to_right="Sounds from left to right. Default is `0.0`",
        right_to_left="Sounds from right to left. Default is `0.0`"
    )
    @commands.dynamic_cooldown(cooldown_check, commands.BucketType.guild)
    async def channelmix(self, ctx: commands.Context, left_to_left: commands.Range[float, 0, 1] = 1.0, right_to_right: commands.Range[float, 0, 1] = 1.0, left_to_right: commands.Range[float, 0, 1] = 0.0, right_to_left: commands.Range[float, 0, 1] = 0.0) -> None:
        "Filter which manually adjusts the panning of the audio."
        player = await check_access(ctx)

        if player.filters.has_filter(filter_tag="channelmix"):
            player.filters.remove_filter(filter_tag="channelmix")
        await player.add_filter(voicelink.ChannelMix(tag="channelmix", left_to_left=left_to_left, right_to_right=right_to_right, left_to_right=left_to_right, right_to_left=right_to_left))
        await ctx.send(player.get_msg('channelmix').format(left_to_left, right_to_right, left_to_right, right_to_left))

    @commands.hybrid_command(name="nightcore", aliases=get_aliases("nightcore"))
    @commands.dynamic_cooldown(cooldown_check, commands.BucketType.guild)
    async def nightcore(self, ctx: commands.Context) -> None:
        "Add nightcore filter into your player."
        player = await check_access(ctx)

        await player.add_filter(voicelink.Timescale.nightcore())
        await ctx.send(player.get_msg('nightcore'))

    @commands.hybrid_command(name="8d", aliases=get_aliases("8d"))
    @commands.dynamic_cooldown(cooldown_check, commands.BucketType.guild)
    async def eightD(self, ctx: commands.Context) -> None:
        "Add 8D filter into your player."
        player = await check_access(ctx)

        await player.add_filter(voicelink.Rotation.nightD())
        await ctx.send(player.get_msg('8d'))

    @commands.hybrid_command(name="vaporwave", aliases=get_aliases("vaporwave"))
    @commands.dynamic_cooldown(cooldown_check, commands.BucketType.guild)
    async def vaporwave(self, ctx: commands.Context) -> None:
        "Add vaporwave filter into your player."
        player = await check_access(ctx)

        await player.add_filter(voicelink.Timescale.vaporwave())
        await ctx.send(player.get_msg('vaporwave'))

    @commands.hybrid_command(name="cleareffect", aliases=get_aliases("cleareffect"))
    @app_commands.describe(effect="Remove a specific sound effects.")
    @app_commands.autocomplete(effect=effect_autocomplete)
    @commands.dynamic_cooldown(cooldown_check, commands.BucketType.guild)
    async def cleareffect(self, ctx: commands.Context, effect: str = None) -> None:
        "Clear all or specific sound effects."
        player = await check_access(ctx)

        if effect:
            await player.remove_filter(effect)
        else:
            await player.reset_filter()
            
        await ctx.send(player.get_msg('cleareffect'))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Effect(bot))
